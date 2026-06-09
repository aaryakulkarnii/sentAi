"""Curated MITRE ATT&CK technique seed.

A compact, dev-friendly subset of Enterprise ATT&CK covering every tactic so
the matrix renders fully without downloading the multi-MB STIX bundle. The full
loader (scripts/load_mitre.py) can replace this in production.
"""

ATTACK_URL = "https://attack.mitre.org/techniques/"


def _u(tid: str) -> str:
    return ATTACK_URL + tid.replace(".", "/") + "/"


# (id, tactic, tactic_id, technique, sub_technique, description, mitigation)
TECHNIQUES = [
    # Initial Access
    ("T1078", "Initial Access", "TA0001", "Valid Accounts", None,
     "Adversaries obtain and abuse credentials of existing accounts to gain access.",
     "Enforce MFA, monitor for anomalous logins, disable dormant accounts."),
    ("T1190", "Initial Access", "TA0001", "Exploit Public-Facing Application", None,
     "Adversaries exploit weaknesses in internet-facing software.",
     "Patch promptly, deploy a WAF, segment exposed services."),
    ("T1566", "Initial Access", "TA0001", "Phishing", None,
     "Adversaries send malicious messages to gain access to victim systems.",
     "User training, email filtering, attachment sandboxing."),
    # Execution
    ("T1059", "Execution", "TA0002", "Command and Scripting Interpreter", None,
     "Adversaries abuse command and script interpreters to execute commands.",
     "Restrict interpreters, application control, log script blocks."),
    ("T1059.001", "Execution", "TA0002", "Command and Scripting Interpreter", "PowerShell",
     "Adversaries abuse PowerShell for execution, discovery, and evasion.",
     "Enable PowerShell logging/AMSI, Constrained Language Mode."),
    ("T1059.003", "Execution", "TA0002", "Command and Scripting Interpreter", "Windows Command Shell",
     "Adversaries abuse cmd.exe to execute commands and scripts.",
     "Application control, command-line auditing."),
    ("T1204", "Execution", "TA0002", "User Execution", None,
     "Adversaries rely on a user opening a malicious file or link.",
     "User training, block risky attachments, sandboxing."),
    # Persistence
    ("T1053", "Persistence", "TA0003", "Scheduled Task/Job", None,
     "Adversaries abuse task scheduling to run malicious code persistently.",
     "Audit scheduled tasks, restrict task creation privileges."),
    ("T1547", "Persistence", "TA0003", "Boot or Logon Autostart Execution", None,
     "Adversaries configure autostart locations to maintain persistence.",
     "Monitor autostart locations, restrict registry modifications."),
    ("T1136", "Persistence", "TA0003", "Create Account", None,
     "Adversaries create accounts to maintain access to systems.",
     "Alert on new account creation, enforce least privilege."),
    # Privilege Escalation
    ("T1068", "Privilege Escalation", "TA0004", "Exploitation for Privilege Escalation", None,
     "Adversaries exploit software vulnerabilities to elevate privileges.",
     "Patch management, exploit protection, least privilege."),
    ("T1548", "Privilege Escalation", "TA0004", "Abuse Elevation Control Mechanism", None,
     "Adversaries bypass controls like UAC or sudo to elevate privileges.",
     "Harden UAC/sudo, monitor elevation events."),
    # Defense Evasion
    ("T1070", "Defense Evasion", "TA0005", "Indicator Removal", None,
     "Adversaries delete or modify artifacts to remove evidence.",
     "Forward logs off-host, restrict log deletion, file integrity monitoring."),
    ("T1562", "Defense Evasion", "TA0005", "Impair Defenses", None,
     "Adversaries disable security tools and logging.",
     "Tamper protection, alert on defense changes."),
    ("T1027", "Defense Evasion", "TA0005", "Obfuscated Files or Information", None,
     "Adversaries obfuscate payloads to evade detection.",
     "Behavioral detection, AMSI, deobfuscation analysis."),
    # Credential Access
    ("T1110", "Credential Access", "TA0006", "Brute Force", None,
     "Adversaries guess credentials via repeated authentication attempts.",
     "Account lockout, MFA, rate limiting, anomaly detection."),
    ("T1110.003", "Credential Access", "TA0006", "Brute Force", "Password Spraying",
     "Adversaries try one password across many accounts to avoid lockout.",
     "MFA, detect distributed auth failures, lockout policy."),
    ("T1003", "Credential Access", "TA0006", "OS Credential Dumping", None,
     "Adversaries dump credentials from the OS to obtain account material.",
     "Credential Guard, restrict SeDebug, monitor LSASS access."),
    ("T1003.001", "Credential Access", "TA0006", "OS Credential Dumping", "LSASS Memory",
     "Adversaries access LSASS memory to extract credentials (e.g. Mimikatz).",
     "Enable Credential Guard, PPL for LSASS, EDR LSASS rules."),
    # Discovery
    ("T1046", "Discovery", "TA0007", "Network Service Discovery", None,
     "Adversaries scan for services/ports to find exploitable systems.",
     "Network segmentation, IDS, rate-limit scanning."),
    ("T1018", "Discovery", "TA0007", "Remote System Discovery", None,
     "Adversaries enumerate other hosts on the network.",
     "Monitor discovery tooling, segment networks."),
    ("T1087", "Discovery", "TA0007", "Account Discovery", None,
     "Adversaries enumerate accounts to inform follow-on activity.",
     "Audit directory queries, limit account enumeration."),
    # Lateral Movement
    ("T1021", "Lateral Movement", "TA0008", "Remote Services", None,
     "Adversaries use valid accounts over remote services to move laterally.",
     "MFA on remote services, network segmentation, session logging."),
    ("T1021.001", "Lateral Movement", "TA0008", "Remote Services", "Remote Desktop Protocol",
     "Adversaries use RDP with valid credentials to move laterally.",
     "Restrict RDP, MFA, monitor 4624 type-10 logons."),
    ("T1570", "Lateral Movement", "TA0008", "Lateral Tool Transfer", None,
     "Adversaries copy tools between systems during an intrusion.",
     "Monitor SMB transfers, restrict admin shares."),
    # Collection
    ("T1005", "Collection", "TA0009", "Data from Local System", None,
     "Adversaries collect data from local system sources.",
     "DLP, file access auditing, least privilege."),
    ("T1560", "Collection", "TA0009", "Archive Collected Data", None,
     "Adversaries compress/encrypt data prior to exfiltration.",
     "Detect archiving utilities, monitor large file operations."),
    # Command and Control
    ("T1071", "Command and Control", "TA0011", "Application Layer Protocol", None,
     "Adversaries use common protocols (HTTP/DNS) to blend C2 traffic.",
     "Proxy inspection, DNS monitoring, TLS inspection."),
    ("T1105", "Command and Control", "TA0011", "Ingress Tool Transfer", None,
     "Adversaries download tools from external systems into the environment.",
     "Egress filtering, block known-bad, monitor downloads."),
    ("T1572", "Command and Control", "TA0011", "Protocol Tunneling", None,
     "Adversaries tunnel C2 within another protocol to evade detection.",
     "Inspect tunneled protocols, anomaly detection."),
    # Exfiltration
    ("T1041", "Exfiltration", "TA0010", "Exfiltration Over C2 Channel", None,
     "Adversaries steal data over the existing C2 channel.",
     "Egress monitoring, DLP, data volume anomaly alerts."),
    ("T1048", "Exfiltration", "TA0010", "Exfiltration Over Alternative Protocol", None,
     "Adversaries exfiltrate data over a protocol distinct from C2.",
     "Egress filtering, DNS/ICMP monitoring."),
    # Impact
    ("T1486", "Impact", "TA0040", "Data Encrypted for Impact", None,
     "Adversaries encrypt data to disrupt availability (ransomware).",
     "Offline backups, behavioral ransomware detection, least privilege."),
    ("T1490", "Impact", "TA0040", "Inhibit System Recovery", None,
     "Adversaries delete backups/shadow copies to prevent recovery.",
     "Protect backups, alert on vssadmin/wbadmin use."),
    # Reconnaissance
    ("T1595", "Reconnaissance", "TA0043", "Active Scanning", None,
     "Adversaries probe victim infrastructure prior to compromise.",
     "Attack-surface monitoring, rate-limit external scans."),
]


def seed_records() -> list[dict]:
    return [
        {
            "id": tid,
            "tactic": tactic,
            "tactic_id": tactic_id,
            "technique": technique,
            "sub_technique": sub,
            "description": desc,
            "mitigation": {"summary": mitigation},
            "url": _u(tid),
        }
        for (tid, tactic, tactic_id, technique, sub, desc, mitigation) in TECHNIQUES
    ]
