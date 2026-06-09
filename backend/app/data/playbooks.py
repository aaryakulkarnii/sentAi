"""Remediation playbooks keyed by MITRE technique.

Used by the Response agent and the RAG knowledge base. Each playbook lists
concrete containment / eradication / recovery steps a SOC analyst would follow.
"""

PLAYBOOKS = {
    "T1110": {
        "title": "Brute Force / Credential Guessing",
        "steps": [
            "Temporarily block the source IP at the firewall / WAF.",
            "Force a password reset for any targeted accounts.",
            "Enable or verify account lockout thresholds.",
            "Require MFA for the affected accounts and service.",
            "Review authentication logs for any successful login from the source IP.",
        ],
    },
    "T1110.003": {
        "title": "Password Spraying",
        "steps": [
            "Identify all accounts targeted from the source IP and check for compromise.",
            "Block the source IP and any related infrastructure.",
            "Enforce MFA org-wide and disable legacy/basic authentication.",
            "Reset passwords for any account that authenticated successfully.",
        ],
    },
    "T1046": {
        "title": "Network Service Scanning",
        "steps": [
            "Block the scanning source IP at the perimeter.",
            "Confirm exposed services are patched and access-controlled.",
            "Verify network segmentation limits lateral reachability.",
            "Add the source IP to a watchlist for follow-on activity.",
        ],
    },
    "T1059.001": {
        "title": "PowerShell Abuse",
        "steps": [
            "Isolate the affected host from the network.",
            "Capture and analyse the PowerShell command line and script blocks.",
            "Enable PowerShell script-block logging and AMSI if not already on.",
            "Hunt for persistence (scheduled tasks, run keys) created by the script.",
        ],
    },
    "T1003.001": {
        "title": "LSASS Credential Dumping",
        "steps": [
            "Immediately isolate the host — assume credentials are compromised.",
            "Reset passwords for all accounts that logged into the host (esp. privileged).",
            "Enable Credential Guard and LSASS protection (RunAsPPL).",
            "Hunt for lateral movement using the dumped credentials.",
        ],
    },
    "T1021.001": {
        "title": "Lateral Movement via RDP",
        "steps": [
            "Review RDP (4624 type-10) logons from the source and disable if unauthorised.",
            "Restrict RDP to jump hosts and enforce MFA.",
            "Isolate affected destination hosts and check for tooling drops.",
        ],
    },
    "T1486": {
        "title": "Ransomware / Data Encrypted for Impact",
        "steps": [
            "Isolate affected hosts immediately to stop spread.",
            "Identify and preserve the ransom note and a sample encrypted file.",
            "Restore from offline backups after confirming eradication.",
            "Determine initial access vector and close it.",
        ],
    },
}

GENERIC_STEPS = [
    "Triage the alert and confirm whether it is a true positive.",
    "Scope the activity: identify all affected hosts, users, and IPs.",
    "Contain by isolating affected assets and blocking malicious infrastructure.",
    "Eradicate the root cause and reset any exposed credentials.",
    "Recover affected systems and document lessons learned.",
]


def playbook_for(technique_id: str | None) -> dict:
    if technique_id and technique_id in PLAYBOOKS:
        return PLAYBOOKS[technique_id]
    # Try the parent technique (strip sub-technique suffix).
    if technique_id and "." in technique_id:
        base = technique_id.split(".")[0]
        if base in PLAYBOOKS:
            return PLAYBOOKS[base]
    return {"title": "General Incident Response", "steps": GENERIC_STEPS}
