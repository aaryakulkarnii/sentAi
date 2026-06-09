# SentinelAI – Product Requirements Document

## Overview

SentinelAI is an AI-powered Security Operations Center (SOC) platform that automates threat detection, investigation, enrichment, risk scoring, incident response, and reporting.

The platform is designed as a production-grade cybersecurity SaaS product inspired by Splunk, QRadar, Microsoft Sentinel, CrowdStrike Falcon, and Palo Alto Cortex.

The system ingests real telemetry from Windows, Linux, cloud environments, and network devices, performs automated security analysis using AI agents, and generates actionable incident investigations.

## Problem Statement

Modern SOC analysts face alert fatigue, massive log volumes, slow investigations, knowledge fragmentation, and manual incident response. Organizations receive thousands of alerts daily. Most alerts are low quality, disconnected, and require hours of manual investigation.

Security teams need a system capable of correlating events, identifying attack chains, providing context, generating reports, and recommending actions without requiring manual investigation.

## Vision

Build an autonomous AI SOC platform capable of:

- Ingesting security telemetry
- Detecting threats
- Correlating attack chains
- Investigating incidents
- Mapping attacks to MITRE ATT&CK
- Retrieving threat intelligence
- Generating remediation plans
- Producing executive reports

The platform functions as an AI SOC analyst rather than a traditional SIEM.

## Target Users

| Persona | Responsibilities | Key Needs |
|---|---|---|
| Tier 1 Analyst | Monitor alerts, triage incidents | Fast context, reduced alert fatigue |
| Tier 2 Analyst | Deep investigations, threat hunting | Attack timelines, MITRE mapping, threat intel |
| SOC Manager | Team oversight, reporting | Executive dashboards, incident metrics |
| Security Engineer | Detection engineering, administration | Sigma rules, data pipelines, integrations |

## Success Metrics

| Category | Metric |
|---|---|
| Technical | Log ingestion latency < 5s, search response < 1s, investigation generation < 30s, 99% uptime |
| Business | Reduce investigation time by 80%, reduce alert fatigue by 60%, improve threat visibility |

## Core Features

### 1. Log Collection Platform

Collect telemetry from Windows (Sysmon, Event Viewer, PowerShell), Linux (Auditd, Syslog, Auth), cloud (CloudTrail, GuardDuty, Azure, GCP), and network devices (Fortinet, Palo Alto, pfSense, Cisco).

Flow: Sources → Beats/Collectors → Kafka → Processing Pipeline

### 2. Normalization Engine

Convert all telemetry into a unified schema with fields: timestamp, user, host, source/dest IP, process, event type, severity. Enrichment: GeoIP, ASN, threat context, asset context.

### 3. Detection Engine

Sigma rules, behavioral rules, and statistical anomalies. Detections include brute force, credential stuffing, privilege escalation, persistence, PowerShell abuse, lateral movement, data exfiltration, and malware execution. Outputs: alert, severity, confidence, MITRE mapping.

### 4. Correlation Engine

Build attack chains from related alerts. Outputs: incident, timeline, attack graph.

### 5. MITRE ATT&CK Integration

Store tactics, techniques, sub-techniques, mitigations. Outputs: ATT&CK matrix visualization, technique explanations.

### 6. Threat Intelligence Platform

Sources: MITRE ATT&CK, CISA, NVD, AbuseIPDB, AlienVault OTX, MalwareBazaar. Features: IOC search, threat actor profiles, malware/CVE intelligence.

### 7. RAG Knowledge Engine

Qdrant vector store with embeddings for CVEs, ATT&CK, threat reports, playbooks. Outputs: threat explanations, incident context, mitigation guidance.

### 8. Multi-Agent Investigation System

LangGraph agents: Threat Hunter, Threat Intelligence, MITRE, Investigation, Response, Executive.

### 9. Risk Scoring Engine

0–100 score from severity, confidence, asset criticality, threat context, exploit availability. Levels: Low, Medium, High, Critical.

### 10. Autonomous Investigation

Workflow: Alert → Investigation Agent → Threat Intel → MITRE → Risk Engine → Response → Executive. Output: complete investigation package.

### 11. Incident Management

Create, assign, escalate, track status, add evidence and notes. States: Open, Investigating, Contained, Resolved, Closed.

### 12. Reporting System

PDF and DOCX reports with executive summary, technical analysis, timeline, ATT&CK mapping, IOCs, and recommendations.

## Frontend Requirements

- Framework: Next.js, TypeScript
- Design: enterprise-grade, premium SOC appearance
- Animations: Framer Motion, animated charts, real-time updates
- Pages: SOC Dashboard, Alert Center, Incident Center, Threat Intelligence, MITRE Matrix, AI Investigation Console, Reports, Settings

## Backend Requirements

FastAPI handling authentication, alert processing, investigation APIs, incident APIs, threat intelligence APIs, and reporting APIs.

## Database Architecture

| Store | Purpose |
|---|---|
| PostgreSQL | Users, incidents, alerts, assets, investigations, reports |
| OpenSearch | Logs, search data |
| Redis | Sessions, cache, behavioral counters |
| Qdrant | Threat intelligence and ATT&CK embeddings |

## Infrastructure

Docker, Docker Compose, AWS (EC2, S3, RDS, OpenSearch).

## MVP Phases

| Phase | Scope |
|---|---|
| Phase 1 | Log ingestion, OpenSearch, detection engine, dashboard |
| Phase 2 | Threat intelligence, MITRE integration, incident management |
| Phase 3 | RAG, AI agents, autonomous investigations |
| Phase 4 | Cloud deployment, advanced analytics, SOAR automation |

## Long-Term Vision

SentinelAI evolves into a fully autonomous AI SOC platform with continuous monitoring, threat hunting, incident response, executive reporting, and security orchestration with minimal analyst intervention.
