"""Threat intelligence connectors with fan-out aggregation and Redis caching.

Each connector degrades gracefully: with no API key it returns a clear
"not configured" result rather than failing, so IOC search always responds.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import re

import httpx
import structlog

from app.core.config import settings
from app.db.redis import get_redis

logger = structlog.get_logger(__name__)

CACHE_TTL = 3600
_HASH_RE = re.compile(r"^[a-fA-F0-9]{32,64}$")
_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$")


def classify_ioc(value: str) -> str:
    value = value.strip()
    try:
        ipaddress.ip_address(value)
        return "ip"
    except ValueError:
        pass
    if _HASH_RE.match(value):
        return "hash"
    if _DOMAIN_RE.match(value):
        return "domain"
    if value.startswith("CVE-") or value.startswith("cve-"):
        return "cve"
    return "unknown"


def _not_configured(source: str, key_name: str) -> dict:
    return {"source": source, "status": "not_configured",
            "detail": f"Set {key_name} to enable this source."}


async def _abuseipdb(client: httpx.AsyncClient, ip: str) -> dict:
    if not settings.ABUSEIPDB_API_KEY:
        return _not_configured("AbuseIPDB", "ABUSEIPDB_API_KEY")
    try:
        r = await client.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": settings.ABUSEIPDB_API_KEY, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
        )
        d = r.json().get("data", {})
        return {"source": "AbuseIPDB", "status": "ok",
                "abuse_score": d.get("abuseConfidenceScore"),
                "country": d.get("countryCode"), "isp": d.get("isp"),
                "total_reports": d.get("totalReports"),
                "domain": d.get("domain")}
    except Exception as exc:
        return {"source": "AbuseIPDB", "status": "error", "detail": str(exc)}


async def _otx(client: httpx.AsyncClient, value: str, ioc_type: str) -> dict:
    if not settings.OTX_API_KEY:
        return _not_configured("AlienVault OTX", "OTX_API_KEY")
    section = {"ip": "IPv4", "domain": "domain", "hash": "file"}.get(ioc_type, "IPv4")
    try:
        r = await client.get(
            f"https://otx.alienvault.com/api/v1/indicators/{section}/{value}/general",
            headers={"X-OTX-API-KEY": settings.OTX_API_KEY},
        )
        d = r.json()
        return {"source": "AlienVault OTX", "status": "ok",
                "pulse_count": d.get("pulse_info", {}).get("count", 0),
                "reputation": d.get("reputation")}
    except Exception as exc:
        return {"source": "AlienVault OTX", "status": "error", "detail": str(exc)}


async def _malwarebazaar(client: httpx.AsyncClient, file_hash: str) -> dict:
    try:
        r = await client.post(
            "https://mb-api.abuse.ch/api/v1/",
            data={"query": "get_info", "hash": file_hash},
        )
        d = r.json()
        if d.get("query_status") != "ok":
            return {"source": "MalwareBazaar", "status": "ok", "found": False}
        info = (d.get("data") or [{}])[0]
        return {"source": "MalwareBazaar", "status": "ok", "found": True,
                "signature": info.get("signature"), "file_type": info.get("file_type"),
                "tags": info.get("tags")}
    except Exception as exc:
        return {"source": "MalwareBazaar", "status": "error", "detail": str(exc)}


async def _nvd(client: httpx.AsyncClient, cve: str) -> dict:
    try:
        r = await client.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={"cveId": cve.upper()},
        )
        items = r.json().get("vulnerabilities", [])
        if not items:
            return {"source": "NVD", "status": "ok", "found": False}
        c = items[0]["cve"]
        metrics = c.get("metrics", {})
        cvss = None
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if key in metrics and metrics[key]:
                cvss = metrics[key][0]["cvssData"].get("baseScore")
                break
        desc = next((d["value"] for d in c.get("descriptions", []) if d["lang"] == "en"), "")
        return {"source": "NVD", "status": "ok", "found": True,
                "cvss": cvss, "description": desc[:300]}
    except Exception as exc:
        return {"source": "NVD", "status": "error", "detail": str(exc)}


async def search_ioc(value: str) -> dict:
    """Fan out across connectors for an IOC, with Redis caching."""
    value = value.strip()
    ioc_type = classify_ioc(value)
    cache_key = f"ti:ioc:{value}"

    redis = get_redis()
    try:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    sources: list[dict] = []
    async with httpx.AsyncClient(timeout=8.0) as client:
        tasks = []
        if ioc_type == "ip":
            tasks = [_abuseipdb(client, value), _otx(client, value, "ip")]
        elif ioc_type == "domain":
            tasks = [_otx(client, value, "domain")]
        elif ioc_type == "hash":
            tasks = [_malwarebazaar(client, value), _otx(client, value, "hash")]
        elif ioc_type == "cve":
            tasks = [_nvd(client, value)]
        if tasks:
            sources = list(await asyncio.gather(*tasks))

    result = {
        "ioc": value,
        "type": ioc_type,
        "verdict": _verdict(sources),
        "sources": sources,
    }

    try:
        await redis.set(cache_key, json.dumps(result), ex=CACHE_TTL)
    except Exception:
        pass
    return result


def _verdict(sources: list[dict]) -> str:
    for s in sources:
        if s.get("status") == "ok":
            if (s.get("abuse_score") or 0) >= 50:
                return "malicious"
            if s.get("found") is True:
                return "malicious"
            if (s.get("pulse_count") or 0) > 0:
                return "suspicious"
    configured = any(s.get("status") == "ok" for s in sources)
    return "clean" if configured else "unknown"
