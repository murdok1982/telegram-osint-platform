# 🛡️ Telegram OSINT/CTI Platform
### Developed by **[MuRDoK-1982-](https://github.com/MuRDoK-1982-)**

![OSINT](https://img.shields.io/badge/Focus-OSINT%20%2F%20CTI-blue?style=for-the-badge&logo=spyderide)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

A modular, auditable, and scalable ecosystem designed for early detection of high-impact risks in public Telegram groups. This platform combines advanced MTProto collection, multi-language rule engines, and AI-driven forensic analysis to provide actionable intelligence.

---

## 🚀 Core Features

### 📡 Hyper-Efficient Collection
*   **Telethon (MTProto)**: High-performance listener for real-time monitoring of public groups and channels.
*   **Privacy by Design**: Mandatory pseudonymization of all user handles using salted SHA-256 hashes.
*   **Selective Acquisition**: Automatic downloading of media only when high-risk scores are detected.

### 🧠 Advanced Logic Engine
*   **Multi-Language Support**: Specialized rule sets for **ES / EN / AR / RU / ZH / KO**.
*   **Intelligence Normalizer**: Decodes *Arabizi* and *Leetspeak* to bypass common evasion techniques.
*   **Obfuscation Detection**: Heuristic analysis for Base64, Hex, and high-entropy secret sharing.
*   **Fuzzy Matching**: High-precision detection of typosquatted or slightly modified keywords.

### 🕵️ Multi-Agent AI Orchestration
*   **Agent A (Forensic Psychology)**: Detects radicalization patterns, coercion, and behavioral risk signals.
*   **Agent B (Threat Intel)**: Evaluates hybrid threats, coordinated campaigns, and infrastructure sabotage.
*   **Agent C (Strategy)**: Consolidates all findings into professional intelligence reports with TTP mapping.

### 📊 Professional Output
*   **Automated PDF Reports**: Detailed executive summaries, risk metrics, and agent assessments.
*   **Direct Alerts**: Secure SMTP delivery of high-risk intelligence cases.
*   **Sherlock Integration**: Integrated OSINT lookup for cross-platform username presence.

---

## 🏗️ Architecture

```mermaid
graph TD
    TC[Telegram Collector] -->|POST /ingest| API[FastAPI Orchestrator]
    API -->|Async Task| CW[Celery Worker]
    CW -->|Rule Engine| RE[Detection Engine]
    RE -->|Score >= 12| AA[AI Analysis Agents]
    AA -->|A / B / C| RG[Report Generator]
    RG -->|PDF| EMAIL[SMTP Alert]
    API -->|Metadata| DB[(PostgreSQL)]
    API -->|Queue| RD[(Redis)]
```

---

## 🛠️ Quick Start

### 1. Requirements
Ensure you have **Docker** and **Docker Compose** installed.

### 2. Configuration
Create a `.env` file based on the provided `.env.example`:
```bash
cp .env.example .env
# Edit .env with your TG_API_ID, TG_API_HASH and OPENAI_API_KEY
```

### 3. Launch
```bash
docker-compose up --build -d
```

---

## ⚖️ Ethical Use & Compliance
This system is designed for **defensive use cases**, law enforcement support, and corporate threat intelligence. It maintains immutable audit logs for every ingestion and analysis action to ensure operational accountability.

---

## 👨‍💻 Author
**MuRDoK-1982-**  
*Senior OSINT/CTI Architect & Python Backend Engineer*

*Disclaimer: This platform belongs to MuRDoK-1982-. Unauthorized distribution is strictly monitored.*

---

## 🎖️ CENTRO DE COMUNICACIONES Y REPORTES OFICIALES
**NIVEL DE ACCESO:** AUTORIZADO | **DESTINATARIO:** COMANDANCIA DE DESARROLLO (gustavolobatoclara@gmail.com)

A través del siguiente portal de comunicaciones, el personal autorizado puede emitir reportes de incidencias, fallas críticas en despliegue (compilación) o solicitudes de mejoras estratégicas. Seleccione la directiva correspondiente para visualizar los protocolos de envío:

<details>
<summary><b>🚨 REPORTAR QUEJA O INCIDENCIA DISCIPLINARIA / OPERATIVA</b></summary>
<br>
Para tramitar una queja sobre el funcionamiento, estructura o contenido del sistema, envíe un mensaje a <b>gustavolobatoclara@gmail.com</b> siguiendo este protocolo:
<ol>
  <li><b>Asunto:</b> [QUEJA] - Nombre del Sistema - Breve descripción.</li>
  <li><b>Cuerpo del mensaje:</b> Detallar claramente la incidencia, impacto operativo y, si es posible, la evidencia (capturas o logs).</li>
  <li><b>Prioridad:</b> Indicar si es de atención inmediata o diferida.</li>
</ol>
</details>

<details>
<summary><b>🛠️ REPORTE DE PROBLEMAS DE COMPILACIÓN O DESPLIEGUE</b></summary>
<br>
Si experimenta fallos durante la fase de compilación o instalación del sistema, reporte a <b>gustavolobatoclara@gmail.com</b> con la siguiente estructura técnica:
<ol>
  <li><b>Asunto:</b> [COMPILACIÓN] - Falla en entorno &lt;Entorno/OS&gt;.</li>
  <li><b>Especificaciones:</b> Sistema Operativo, versión de dependencias y herramientas de compilación utilizadas.</li>
  <li><b>Traza de Error (Logs):</b> Adjunte el log completo de errores proporcionado por la terminal (en formato texto o captura legible).</li>
  <li><b>Pasos de Reproducción:</b> Secuencia exacta de comandos ejecutados antes del fallo crítico.</li>
</ol>
</details>

<details>
<summary><b>💡 SUGERENCIAS O SOLICITUDES DE DESARROLLO</b></summary>
<br>
Para proponer nuevas capacidades tácticas, módulos de inteligencia o mejoras de arquitectura, envíe su solicitud a <b>gustavolobatoclara@gmail.com</b>:
<ol>
  <li><b>Asunto:</b> [PROPUESTA] - Mejora o Nuevo Módulo.</li>
  <li><b>Objetivo Táctico:</b> ¿Qué problema resuelve o qué ventaja proporciona esta nueva característica?</li>
  <li><b>Viabilidad:</b> (Opcional) Posible enfoque técnico o herramientas recomendadas para su implementación.</li>
</ol>
</details>

---
