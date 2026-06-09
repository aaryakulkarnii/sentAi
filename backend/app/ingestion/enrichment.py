"""GeoIP / ASN enrichment for normalised events."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings
from app.ingestion.schema import NormalizedEvent

logger = structlog.get_logger(__name__)

# geoip2 is an optional dependency; enrichment is skipped if it's unavailable.
try:
    import geoip2.database
    import geoip2.errors

    _GEOIP_AVAILABLE = True
except ImportError:
    _GEOIP_AVAILABLE = False

_city_reader: Any | None = None
_asn_reader: Any | None = None


def _open_reader(path: str) -> Any | None:
    if not _GEOIP_AVAILABLE:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return geoip2.database.Reader(str(p))
    except Exception as exc:
        logger.warning("geoip_open_failed", path=path, error=str(exc))
        return None


def init_geoip() -> None:
    global _city_reader, _asn_reader
    if not _GEOIP_AVAILABLE:
        logger.info("geoip_unavailable")
        return
    _city_reader = _open_reader(settings.GEOIP_DB_PATH)
    _asn_reader = _open_reader(settings.GEOIP_ASN_DB_PATH)
    if _city_reader:
        logger.info("geoip_city_loaded", path=settings.GEOIP_DB_PATH)
    else:
        logger.info("geoip_city_unavailable", path=settings.GEOIP_DB_PATH)


def enrich(event: NormalizedEvent) -> NormalizedEvent:
    """Enrich event with GeoIP/ASN data when databases are available."""
    ip = event.source_ip
    if not ip or not _city_reader:
        return event

    try:
        record = _city_reader.city(ip)
        event.geo_country = record.country.iso_code
        event.geo_city = record.city.name
    except geoip2.errors.AddressNotFoundError:
        pass
    except Exception as exc:
        logger.debug("geoip_lookup_failed", ip=ip, error=str(exc))

    if _asn_reader:
        try:
            asn = _asn_reader.asn(ip)
            event.asn = f"AS{asn.autonomous_system_number}"
        except geoip2.errors.AddressNotFoundError:
            pass
        except Exception as exc:
            logger.debug("asn_lookup_failed", ip=ip, error=str(exc))

    return event
