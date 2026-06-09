# 🛡️ SentinelAI

<div align="center">

### Autonomous AI-Powered Security Operations Center

Detect • Investigate • Correlate • Respond

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge\&logo=nextdotjs\&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge\&logo=typescript\&logoColor=white)](https://typescriptlang.org)
[![Kafka](https://img.shields.io/badge/Kafka-231F20?style=for-the-badge\&logo=apachekafka\&logoColor=white)](https://kafka.apache.org)
[![OpenSearch](https://img.shields.io/badge/OpenSearch-005EB8?style=for-the-badge\&logo=opensearch\&logoColor=white)](https://opensearch.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge\&logo=docker\&logoColor=white)](https://docker.com)

### AI-Native Threat Detection & Investigation Platform

Built to automate the modern Security Operations Center using AI agents, threat intelligence, attack correlation, and autonomous investigations.

</div>

---

# Overview

Traditional SIEM platforms generate thousands of alerts every day, forcing analysts to manually investigate incidents across multiple tools.

SentinelAI reimagines Security Operations by combining:

* Real-time log ingestion
* Threat detection
* Incident correlation
* MITRE ATT&CK mapping
* Threat intelligence enrichment
* Multi-agent AI investigations
* Executive reporting

into a single AI-native platform.

The goal is simple:

> Reduce analyst workload while improving detection accuracy and response speed.

---

# Key Features

## 🔍 Threat Detection Engine

Detects threats using:

* Sigma Rules
* Behavioral Analytics
* Statistical Anomaly Detection
* Correlation Rules
* IOC Matching

Supports detection of:

* Brute Force Attacks
* Password Spraying
* Credential Stuffing
* Privilege Escalation
* PowerShell Abuse
* Mimikatz Activity
* Lateral Movement
* Persistence Techniques
* Malware Execution
* Data Exfiltration

---

## 🧠 AI Investigation Pipeline

Powered by LangGraph multi-agent workflows.

### Investigation Agents

1. Threat Hunter Agent
2. Threat Intelligence Agent
3. MITRE ATT&CK Mapper
4. Incident Investigator
5. Response Advisor
6. Executive Summary Agent

Each incident passes through all agents automatically, generating a complete investigation report.

---

## ⚔️ MITRE ATT&CK Integration

Every alert is mapped to:

* Tactics
* Techniques
* Sub-Techniques

Includes:

* ATT&CK Matrix Visualization
* Detection Coverage Mapping
* Technique Descriptions
* Mitigation Recommendations

---

## 🌍 Threat Intelligence

IOC enrichment using:

* AbuseIPDB
* AlienVault OTX
* MalwareBazaar
* NVD CVE Database

Additional enrichment:

* GeoIP
* ASN Lookup
* Reputation Scores
* Exploit Availability

---

## 📊 Incident Management

Complete incident lifecycle:

Open → Investigating → Contained → Resolved → Closed

Features:

* Analyst Assignment
* Notes
* Evidence Collection
* Timeline Tracking
* Report Generation
* Escalation Workflow

---

## 📚 Security Knowledge Base

Vector-powered RAG system using Qdrant.

Knowledge sources include:

* MITRE ATT&CK
* CVE Database
* Security Playbooks
* Threat Actor Reports
* Malware Analysis Reports

This enables context-aware investigations and explanations.

---

# System Architecture

```text
Telemetry Sources
│
├── Windows Sysmon
├── Event Viewer
├── Linux auditd
├── AWS CloudTrail
├── Azure Logs
├── Network Devices
│
▼

Kafka Event Bus
│
▼

Detection Pipeline
│
├── Normalization
├── Threat Detection
├── Correlation
└── Risk Scoring
│
▼

AI Investigation Pipeline
│
├── Threat Hunter
├── Threat Intel
├── MITRE Mapper
├── Investigator
├── Response Advisor
└── Executive Summary
│
▼

Storage Layer
│
├── PostgreSQL
├── OpenSearch
├── Redis
└── Qdrant
│
▼

FastAPI Backend
│
▼

Next.js Dashboard
```

---

# Technology Stack

| Layer           | Technology                           |
| --------------- | ------------------------------------ |
| Frontend        | Next.js 14, TypeScript, Tailwind CSS |
| Backend         | FastAPI, Python 3.11                 |
| AI Framework    | LangGraph, LangChain                 |
| LLM             | GPT-4o                               |
| Database        | PostgreSQL                           |
| Search          | OpenSearch                           |
| Cache           | Redis                                |
| Vector Database | Qdrant                               |
| Streaming       | Apache Kafka                         |
| Containers      | Docker                               |
| Infrastructure  | AWS                                  |

---

# Screenshots

## Dashboard

```text
docs/images/dashboard.png
```

## Investigation Workflow

```text
docs/images/investigation.png
```

## MITRE ATT&CK Matrix

```text
docs/images/mitre.png
```

---

# Capabilities

| Capability          | Status |
| ------------------- | ------ |
| Log Ingestion       | ✅      |
| Threat Detection    | ✅      |
| Alert Correlation   | ✅      |
| Risk Scoring        | ✅      |
| MITRE ATT&CK        | ✅      |
| AI Investigations   | ✅      |
| Incident Management | ✅      |
| RAG Knowledge Base  | ✅      |
| Threat Intelligence | 🚧     |
| SOAR Automation     | 🚧     |
| Cloud Connectors    | 🚧     |
| Multi-Tenancy       | 🚧     |

---

# Project Structure

```text
sentinelai/

├── backend/
├── frontend/
├── infra/
├── ingestion/
├── scripts/
├── data/
├── docs/
└── tests/
```

---

# Quick Start

## Clone Repository

```bash
git clone https://github.com/aaryakulkarnii/sentinelai.git

cd sentinelai
```

---

## Configure Environment

```bash
cp .env.example .env
```

Add:

```env
OPENAI_API_KEY=
SECRET_KEY=
POSTGRES_PASSWORD=
```

---

## Start Infrastructure

```bash
docker compose up -d
```

---

## Seed Database

```bash
python scripts/seed_db.py
```

---

## Load MITRE Data

```bash
python scripts/load_mitre.py
```

---

## Open Applications

Dashboard:

```text
http://localhost:3000
```

API Docs:

```text
http://localhost:8000/docs
```

OpenSearch:

```text
http://localhost:5601
```

---

# Example Investigation Workflow

1. Suspicious PowerShell command detected
2. Sigma rule triggers alert
3. Correlation engine links related events
4. Risk score generated
5. AI investigation launched
6. MITRE ATT&CK techniques identified
7. Threat intelligence enrichment performed
8. Incident report generated
9. Analyst receives complete findings

---

# Future Roadmap

## Phase 1

* Threat Detection Engine
* Correlation Engine
* Incident Dashboard
* MITRE ATT&CK Mapping

## Phase 2

* Threat Intelligence Integrations
* PDF/DOCX Reporting
* Cloud Source Connectors

## Phase 3

* Autonomous SOAR Actions
* Firewall Blocking
* User Isolation
* Multi-Tenant Support

## Phase 4

* Autonomous Threat Hunting
* AI Red Team Simulations
* Advanced Behavioral Analytics

---

# Why SentinelAI?

Unlike traditional SIEMs that only generate alerts, SentinelAI performs investigations.

The platform is designed to act like a Tier-1 and Tier-2 SOC analyst by:

* Understanding alerts
* Gathering context
* Mapping attacker behavior
* Recommending actions
* Generating reports

This dramatically reduces investigation time and alert fatigue.

---

# Highlights

* AI-Native Security Platform
* LangGraph Multi-Agent Architecture
* MITRE ATT&CK Integration
* Kafka-Based Event Streaming
* OpenSearch Security Analytics
* Vector Search with Qdrant
* FastAPI + Next.js Full Stack Architecture
* Production-Oriented System Design

---

# Contributing

Contributions are welcome.

```bash
git checkout -b feature/my-feature
git commit -m "add feature"
git push origin feature/my-feature
```

Open a Pull Request.

---

# License

MIT License

---

<div align="center">

### Built for the Future of Security Operations

FastAPI • Next.js • LangGraph • Kafka • OpenSearch • Qdrant

</div>
