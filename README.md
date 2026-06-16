# 🛡️ Telegram OSINT/CTI Platform

<div align="center">

![OSINT](https://img.shields.io/badge/OSINT-CTI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-DC3823?style=for-the-badge&logo=redis)
![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

**Plataforma modular de inteligencia de fuentes abiertas (OSINT) y contrainteligencia (CTI) para monitoreo de Telegram**

*Detección temprana de riesgos de alto impacto en grupos públicos de Telegram mediante MTProto, motores de reglas multi-idioma y análisis forense con IA*

</div>

---

## 📋 Tabla de Contenidos

- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Mapa Mental del Proyecto](#-mapa-mental-del-proyecto)
- [Características Principales](#-características-principales)
- [Requisitos](#-requisitos)
- [Instalación Rápida](#-instalación-rápida)
- [Configuración Detallada](#-configuración-detallada)
- [Uso y Operación](#-uso-y-operación)
- [API Reference](#-api-reference)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Desarrollo y Tests](#-desarrollo-y-tests)
- [Seguridad](#-seguridad)
- [Troubleshooting](#-troubleshooting)

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Flujo Principal

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TELEGRAM OSINT/CTI PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                  │
│  │   TELEGRAM   │      │  ORCHESTRATOR│      │    CELERY    │                  │
│  │  COLLECTOR   │─────▶│     API      │─────▶│    WORKER    │                  │
│  │  (Telethon)  │      │  (FastAPI)   │      │  (Análisis)  │                  │
│  └──────────────┘      └──────────────┘      └──────────────┘                  │
│         │                     │                     │                           │
│         │                     │                     ▼                           │
│         │                     │            ┌──────────────┐                    │
│         │                     │            │    ENGINE    │                    │
│         │                     │            │  (Detector)  │                    │
│         │                     │            └──────────────┘                    │
│         │                     │                     │                           │
│         │                     ▼                     ▼                           │
│         │            ┌──────────────┐      ┌──────────────┐                    │
│         │            │  PostgreSQL  │      │    AGENTS    │                    │
│         │            │     (DB)     │      │   (OpenAI)   │                    │
│         │            └──────────────┘      └──────────────┘                    │
│         │                     │                     │                           │
│         │                     ▼                     ▼                           │
│         │            ┌──────────────┐      ┌──────────────┐                    │
│         │            │    REDIS     │      │  REPORTING   │                    │
│         │            │   (Queue)    │      │  (PDF/DOCX)  │                    │
│         │            └──────────────┘      └──────────────┘                    │
│         │                                                      │                │
│         ▼                                                      ▼                │
│  ┌──────────────┐                                    ┌──────────────┐          │
│  │   DASHBOARD  │                                    │    EMAIL     │          │
│  │    (Web)     │                                    │   (SMTP)     │          │
│  └──────────────┘                                    └──────────────┘          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Completo

```mermaid
graph TD
    A[Telegram Groups/Channels] -->|MTProto| B[Collector - Telethon]
    B -->|Pseudonimiza usuarios| C[POST /ingest/message]
    C -->|Almacena en DB| D[(PostgreSQL)]
    C -->|Encola tarea| E[Redis Queue]
    E -->|Procesa async| F[Celery Worker]
    F -->|Analiza con reglas| G[Engine Detector]
    G -->|Normaliza texto| H[Normalizers]
    G -->|Detecta crypto| I[Crypto Heuristics]
    G -->|Calcula score| J[Risk Score]
    J -->|Score >= 12| K[Crea Caso]
    K -->|Dispara agentes| L[Agent A - Psicología]
    K -->|Dispara agentes| M[Agent B - Inteligencia]
    L -->|Consolida| N[Agent C - Estrategia]
    M -->|Consolida| N
    N -->|Genera reporte| O[PDF Generator]
    N -->|Genera reporte| P[DOCX Generator]
    O -->|Adjunta| Q[Email SMTP]
    P -->|Adjunta| Q
    Q -->|Alerta| R[Analista]
    
    S[Dashboard Web] -->|Consulta| T[API Endpoints]
    T -->|Lee| D
    
    U[Celery Beat] -->|Cada 30min| V[Agrega riesgo por usuario]
    U -->|Cada 24h| W[Limpia mensajes antiguos]
    U -->|Cada 1h| X[Detecta casos stale]
```

### Diagrama de Red Docker

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOCKER NETWORKS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐       ┌─────────────────────┐         │
│  │   NETWORK: backend  │       │    NETWORK: app     │         │
│  │   (Interna - DB)    │       │   (API + Collector) │         │
│  │                     │       │                     │         │
│  │  ┌───────────────┐  │       │  ┌───────────────┐  │         │
│  │  │  PostgreSQL   │  │       │  │  Orchestrator │  │         │
│  │  │    :5432      │  │       │  │     :8000     │  │         │
│  │  └───────────────┘  │       │  └───────────────┘  │         │
│  │         ▲           │       │         ▲           │         │
│  │         │           │       │         │           │         │
│  │  ┌───────────────┐  │       │  ┌───────────────┐  │         │
│  │  │    Redis      │  │       │  │   Collector   │  │         │
│  │  │    :6379      │  │       │  │  (Telethon)   │  │         │
│  │  └───────────────┘  │       │  └───────────────┘  │         │
│  │         ▲           │       │         │           │         │
│  │         │           │       │         │           │         │
│  │  ┌──────┴───────┐   │       │  ┌──────┴───────┐   │         │
│  │  │   Worker     │   │       │  │    Beat      │   │         │
│  │  │  (Celery)    │   │       │  │  (Scheduler) │   │         │
│  │  └──────────────┘   │       │  └──────────────┘   │         │
│  │         ▲           │       │                     │         │
│  └─────────┼───────────┘       └─────────────────────┘         │
│            │                                                   │
│            └───────────────────────────────────────────────────┘
│                                                                 │
│  PUERTO EXPUESTO: 8000 (Dashboard + API)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Mapa Mental del Proyecto

```
                                    ┌─────────────────────────────────────┐
                                    │   TELEGRAM OSINT/CTI PLATFORM       │
                                    │         v1.1.0 - MuRDoK             │
                                    └─────────────────┬───────────────────┘
                                                      │
            ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
            │                                         │                                         │
    ┌───────┴────────┐                      ┌─────────┴─────────┐                      ┌────────┴────────┐
    │   COLLECTOR    │                      │   ORCHESTRATOR    │                      │    REPORTING    │
    │   (Telegram)   │                      │      (API)        │                      │    (Output)     │
    └───────┬────────┘                      └─────────┬─────────┘                      └────────┬────────┘
            │                                         │                                         │
    ┌───────┴────────┐              ┌─────────────────┼─────────────────┐              ┌────────┴────────┐
    │   Telethon     │              │                 │                 │              │   PDF Generator │
    │   MTProto      │              │                 │                 │              │   DOCX Generator│
    │   Pseudonimiza │              │                 │                 │              │   Email SMTP    │
    │   Filtro chats │              │                 │                 │              │   Sherlock OSINT│
    └────────────────┘              │                 │                 │              └─────────────────┘
                                    │                 │                 │
                            ┌───────┴───────┐ ┌───────┴───────┐ ┌──────┴────────┐
                            │   FastAPI     │ │  PostgreSQL   │ │    Redis      │
                            │   JWT Auth    │ │   SQLAlchemy  │ │   Celery      │
                            │   CORS        │ │   Models      │ │   Queue       │
                            │   RBAC        │ │   Migrations  │ │   Cache       │
                            └───────────────┘ └───────────────┘ └───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────┴───────┐ ┌─────┴─────┐ ┌──────┴──────┐
            │    ENGINE     │ │  AGENTS   │ │   CELERY    │
            │  (Detector)   │ │  (OpenAI) │ │   BEAT      │
            └───────┬───────┘ └─────┬─────┘ └──────┬──────┘
                    │               │               │
        ┌───────────┼───────────┐   │       ┌──────┼──────┐
        │           │           │   │       │             │
┌───────┴──────┐ ┌──┴───┐ ┌────┴───┴──┐ ┌──┴───┐ ┌──────┴──────┐
│  Normalizers │ │Crypto│ │ Correlator│ │Agent │ │   Tasks     │
│  - Arabic    │ │Heuris│ │ - Risk    │ │  A   │ │ - Aggregate │
│  - Leet      │ │tics  │ │ - User    │ │  B   │ │ - Cleanup   │
│  - Common    │ │      │ │ - Window  │ │  C   │ │ - Stale     │
└──────────────┘ └──────┘ └───────────┘ └──────┘ └─────────────┘
        │
┌───────┴────────────────────────────────────────────────────────┐
│                        RULES (YAML)                            │
├────────────────────────────────────────────────────────────────┤
│  🇪🇸 es.yaml  │  🇬🇧 en.yaml  │  🇸🇦 ar.yaml  │              │
│  🇷🇺 ru.yaml  │  🇨🇳 zh.yaml  │  🇰🇷 ko.yaml  │              │
├────────────────────────────────────────────────────────────────┤
│  phrases_high_risk  │  keywords_medium_risk  │  regex          │
│  euphemisms         │  slang_regional        │  emoji          │
│  behavioral_patterns│  arabizi               │  topic_buckets  │
└────────────────────────────────────────────────────────────────┘
```

---

## ✨ Características Principales

### 📡 Recolección Hyper-Eficiente
- **Telethon (MTProto)**: Listener de alto rendimiento para monitoreo en tiempo real
- **Privacy by Design**: Pseudonimización obligatoria de handles con SHA-256 + salt
- **Filtro de chats**: Monitoreo selectivo de grupos/canales específicos
- **Adquisición selectiva**: Descarga de media solo cuando se detecta alto riesgo

### 🧠 Motor de Lógica Avanzado
- **Soporte multi-idioma**: Reglas especializadas para **ES / EN / AR / RU / ZH / KO**
- **Normalizador de inteligencia**: Decodifica *Arabizi* y *Leetspeak*
- **Detección de ofuscación**: Análisis heurístico de Base64, Hex y alta entropía
- **Fuzzy matching**: Detección de precisión de keywords ligeramente modificados

### 🕵️ Orquestación Multi-Agente IA
- **Agente A (Psicología Forense)**: Detecta patrones de radicalización, coerción, grooming
- **Agente B (Threat Intel)**: Evalúa amenazas híbridas, campañas coordinadas, sabotaje
- **Agente C (Estrategia)**: Consolida hallazgos en reportes profesionales con TTP mapping

### 📊 Output Profesional
- **Reportes PDF automáticos**: Resúmenes ejecutivos, métricas de riesgo, análisis de agentes
- **Reportes DOCX**: Formato editable para integración con sistemas de inteligencia
- **Alertas directas**: Entrega SMTP segura de casos de inteligencia de alto riesgo
- **Dashboard web**: Interfaz gráfica para gestión de casos, mensajes y estadísticas
- **Integración Sherlock**: Búsqueda OSINT cross-platform de usernames

### 🔒 Seguridad
- **Autenticación JWT**: Tokens con expiración configurable
- **RBAC**: Roles de usuario (admin, analyst, viewer)
- **Auth service-to-service**: API key interna para collector → API
- **Redis con password**: Autenticación en cola de mensajes
- **Contenedores non-root**: Dockerfiles con usuario no privilegiado
- **Redes aisladas**: Segmentación backend/app en Docker

---

## 📋 Requisitos

### Sistema
- **Docker** y **Docker Compose** instalados
- **Python 3.11+** (solo para desarrollo local)
- **8GB RAM** mínimo recomendado
- **10GB** espacio en disco

### Cuentas necesarias
| Servicio | URL | Propósito |
|----------|-----|-----------|
| Telegram API | https://my.telegram.org | Obtener `TG_API_ID` y `TG_API_HASH` |
| OpenAI | https://platform.openai.com | Obtener `OPENAI_API_KEY` para agentes IA |
| SMTP (opcional) | Tu proveedor email | Para alertas por correo |

---

## 🚀 Instalación Rápida

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/murdok1982/telegram-osint-platform.git
cd telegram-osint-platform
```

### Paso 2: Generar archivo .env con claves seguras

```bash
python setup.py
```

Este script genera automáticamente:
- `SECRET_KEY` (64 caracteres hex)
- `INTERNAL_API_KEY` (64 caracteres hex)
- `HASH_SALT` (32 caracteres hex)
- `REDIS_PASSWORD` (32 caracteres hex)
- `DB_PASSWORD` (32 caracteres hex)

### Paso 3: Editar .env con tus credenciales

```bash
# Abrir .env y completar los campos obligatorios:

# Telegram API (OBLIGATORIO)
TG_API_ID=tu_api_id_aqui
TG_API_HASH=tu_api_hash_aqui

# OpenAI API (OBLIGATORIO para agentes IA)
OPENAI_API_KEY=sk-tu_openai_key_aqui

# Opcional: SMTP para alertas por email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
REPORT_RECEIVER=analista@empresa.com

# Opcional: Filtrar chats específicos (vacío = todos)
MONITORED_CHATS=-1001234567890,-1009876543210
```

### Paso 4: Levantar el stack Docker

```bash
docker compose up --build -d
```

### Paso 5: Verificar que todo está corriendo

```bash
docker compose ps
```

Deberías ver 6 servicios activos:
```
NAME                    STATUS
telegram-db-1           Up (healthy)
telegram-redis-1        Up (healthy)
telegram-orchestrator-1 Up
telegram-worker-1       Up
telegram-beat-1         Up
telegram-collector-1    Up
```

### Paso 6: Acceder al Dashboard

Abre tu navegador en: **http://localhost:8000**

---

## ⚙️ Configuración Detallada

### Variables de Entorno (.env)

| Variable | Obligatorio | Descripción | Ejemplo |
|----------|:-----------:|-------------|---------|
| `TG_API_ID` | ✅ | API ID de Telegram | `12345678` |
| `TG_API_HASH` | ✅ | API Hash de Telegram | `abcdef1234567890` |
| `OPENAI_API_KEY` | ✅ | API Key de OpenAI | `sk-...` |
| `SECRET_KEY` | ✅ | Clave para firmar JWT (generada por setup.py) | `a1b2c3...` |
| `INTERNAL_API_KEY` | ✅ | Clave interna collector→API (generada) | `x9y8z7...` |
| `HASH_SALT` | ✅ | Salt para pseudonimización (generada) | `f1e2d3...` |
| `REDIS_PASSWORD` | ✅ | Password de Redis (generada) | `p4s5w6...` |
| `DB_USER` | ❌ | Usuario PostgreSQL | `postgres` |
| `DB_PASSWORD` | ❌ | Password PostgreSQL (generada) | `d1b2p3...` |
| `DB_NAME` | ❌ | Nombre de la base de datos | `telegram_osint` |
| `CORS_ORIGINS` | ❌ | Orígenes CORS (separados por coma) | `http://localhost:3000` |
| `MONITORED_CHATS` | ❌ | IDs de chats a monitorear (vacío=todos) | `-100123,-100456` |
| `SMTP_SERVER` | ❌ | Servidor SMTP para alertas | `smtp.gmail.com` |
| `SMTP_PORT` | ❌ | Puerto SMTP | `587` |
| `SMTP_USER` | ❌ | Usuario SMTP | `alertas@empresa.com` |
| `SMTP_PASSWORD` | ❌ | Password SMTP | `app_password` |
| `REPORT_RECEIVER` | ❌ | Email receptor de reportes | `analista@empresa.com` |

### Configuración de Reglas (rules/*.yaml)

Cada archivo de idioma contiene:

```yaml
language: "es"
version: "3.0"

# Pesos por categoría de amenaza
topic_buckets:
  - category: "extremismo_violento"
    weight: 2.6
  - category: "narcotrafico"
    weight: 2.0

# Indicadores emoji
emoji_indicators:
  weight: 0.8
  items: ["💣","🧨","🔫","🗡️"]

# Eufemismos detectados
euphemisms:
  weight: 1.4
  items: ["el paquete", "la mercancia", "la fiesta"]

# Slang regional
slang_regional:
  weight: 1.6
  items: ["mulas", "puntos", "hierba", "farlopa"]

# Frases de alto riesgo
phrases_high_risk:
  weight: 3.0
  items: ["atentar contra", "celula durmiente", "lobo solitario"]

# Keywords de riesgo medio
keywords_medium_risk:
  weight: 2.0
  items: ["bomba", "explosivos", "arma", "ataque"]

# Patrones regex
regex_indicators:
  weight: 2.2
  items:
    - "(celula\\s?durmiente|lobo\\s?solitario)"
    - "(envio\\s?de\\s?armas|trafico\\s?de\\s?armas)"

# Patrones comportamentales
behavioral_patterns:
  weight: 2.2
  intent_markers: ["voy a", "vamos a", "pronto"]
  recruitment_markers: ["hablame por privado", "unete"]
  logistics_markers: ["entrega", "punto de encuentro"]
```

---

## 📖 Uso y Operación

### 1. Primer acceso al Dashboard

1. Abre **http://localhost:8000**
2. Haz clic en "Regístrate"
3. Completa el formulario:
   - Usuario: `tu_usuario`
   - Email: `tu@email.com`
   - Nombre completo: `Tu Nombre`
   - Contraseña: mínimo 8 caracteres
4. Inicia sesión con tus credenciales

### 2. Dashboard Principal

![Dashboard Concept](https://via.placeholder.com/800x400/1a1a2e/4fc3f7?text=Dashboard+OSINT%2FCTI)

El dashboard muestra:
- **Total de mensajes** monitoreados
- **Total de casos** generados
- **Casos abiertos** pendientes de análisis
- **Mensajes de alto riesgo** detectados
- **Distribución de riesgo** (gráfico de barras)

### 3. Gestión de Casos

```
┌─────────────────────────────────────────────────────────────────┐
│                        CASOS                                    │
├─────────────────────────────────────────────────────────────────┤
│  Filtros: [Todos los estados ▼]  [Actualizar]                  │
├─────┬───────────┬────────┬──────────────────┬──────────────────┤
│ ID  │  Estado   │ Riesgo │   Usuario Hash   │     Fecha        │
├─────┼───────────┼────────┼──────────────────┼──────────────────┤
│  1  │ 🔴 Abierto│  18.5  │ abc123def456...  │ 2024-01-15 14:30 │
│  2  │ 🟡Anális. │  12.2  │ 789xyz012abc...  │ 2024-01-15 13:15 │
│  3  │ 🟢Analiz. │   8.7  │ def456ghi789...  │ 2024-01-15 12:00 │
└─────┴───────────┴────────┴──────────────────┴──────────────────┘
```

**Estados de casos:**
- 🔴 **open**: Caso recién creado, pendiente de análisis
- 🟡 **analyzing**: Agentes IA procesando el caso
- 🟢 **analyzed**: Análisis completado, reporte generado
- ⚫ **closed**: Caso cerrado por analista
- ⚠️ **error**: Error durante el procesamiento

### 4. Ver detalle de un caso

1. Haz clic en "Ver" en la columna Acciones
2. Se abre un modal con:
   - Estado actual
   - Score de riesgo
   - Resumen del caso
   - Análisis de los 3 agentes (A, B, C)
3. Puedes cambiar el estado del caso desde el modal

### 5. Exportar reportes

Desde la API o el dashboard (futuro):

```bash
# Exportar caso como PDF
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/cases/1/export/pdf \
  -o case_1.pdf

# Exportar caso como DOCX
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/cases/1/export/docx \
  -o case_1.docx
```

### 6. Buscar mensajes

```
┌─────────────────────────────────────────────────────────────────┐
│                      MENSAJES                                   │
├─────────────────────────────────────────────────────────────────┤
│  Chat ID: [___________]  User Hash: [___________]  [Buscar]    │
├─────┬───────────┬──────────────────────────────┬────────┬───────┤
│ ID  │   Chat    │            Texto             │ Riesgo │ Fecha │
├─────┼───────────┼──────────────────────────────┼────────┼───────┤
│  1  │ -10012345 │ "voy a atentar contra..."    │ 🔴 18.5│ 14:30 │
│  2  │ -10012345 │ "trae el paquete a la..."    │ 🟡 12.2│ 13:15 │
│  3  │ -10067890 │ "hola buen dia como..."      │ 🟢  0.0│ 12:00 │
└─────┴───────────┴──────────────────────────────┴────────┴───────┘
```

### 7. Tareas programadas (Celery Beat)

El sistema ejecuta automáticamente:

| Tarea | Frecuencia | Descripción |
|-------|------------|-------------|
| `aggregate_user_risk` | Cada 30 min | Agrega riesgo por usuario en ventana de 3h |
| `cleanup_old_messages` | Diario 03:00 | Elimina mensajes > 90 días |
| `check_stale_cases` | Cada hora | Flag cases en "analyzing" > 24h |

Ver logs de Beat:
```bash
docker compose logs -f beat
```

---

## 🔌 API Reference

### Autenticación

Todos los endpoints (excepto `/auth/*` y `/health`) requieren JWT:

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "tu_usuario", "password": "tu_password"}'

# Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {...}
}

# Usar token en requests
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/cases
```

### Endpoints principales

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|:----:|
| `POST` | `/auth/register` | Registrar usuario | ❌ |
| `POST` | `/auth/login` | Login y obtener JWT | ❌ |
| `GET` | `/auth/me` | Info del usuario actual | ✅ |
| `GET` | `/cases` | Listar casos (paginado) | ✅ |
| `GET` | `/cases/{id}` | Detalle de caso | ✅ |
| `PUT` | `/cases/{id}` | Actualizar caso | ✅ |
| `GET` | `/cases/{id}/export/pdf` | Exportar caso PDF | ✅ |
| `GET` | `/cases/{id}/export/docx` | Exportar caso DOCX | ✅ |
| `GET` | `/messages` | Listar mensajes | ✅ |
| `GET` | `/messages/{id}` | Detalle de mensaje | ✅ |
| `GET` | `/stats/dashboard` | Estadísticas globales | ✅ |
| `GET` | `/health` | Estado del sistema | ✅ |
| `POST` | `/ingest/message` | Ingestar mensaje (interno) | 🔑 API Key |

### Ejemplos de uso

```bash
# Listar casos abiertos
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/cases?status=open"

# Actualizar estado de caso
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "closed", "summary": "Falso positivo"}' \
  http://localhost:8000/cases/1

# Obtener estadísticas
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/stats/dashboard

# Health check
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/health
```

---

## 📁 Estructura del Proyecto

```
telegram-osint-platform/
│
├── 📄 docker-compose.yml          # Orquestación de servicios
├── 📄 .env.example                # Plantilla de variables de entorno
├── 📄 .env                        # Variables reales (NO commitear)
├── 📄 setup.py                    # Script de inicialización
├── 📄 README.md                   # Este archivo
│
├── 📂 orchestrator_api/           # API FastAPI principal
│   ├── 📄 main.py                 # Endpoints y configuración
│   ├── 📄 worker.py               # Celery worker (análisis)
│   ├── 📄 beat_worker.py          # Celery Beat (tareas programadas)
│   ├── 📄 database.py             # Conexión SQLAlchemy
│   ├── 📄 models.py               # Modelos DB (Message, Case, AuditLog)
│   ├── 📄 schemas.py              # Schemas Pydantic
│   ├── 📄 auth.py                 # JWT y autenticación
│   ├── 📄 user_models.py          # Modelo User
│   ├── 📄 user_schemas.py         # Schemas User
│   ├── 📄 user_router.py          # Router /auth/*
│   ├── 📄 agents_connector.py     # Conexión a agentes IA
│   ├── 📄 hispan_shield_guardian.py # Auditoría de arranque
│   ├── 📄 Dockerfile              # Imagen API
│   ├── 📄 requirements.txt        # Dependencias Python
│   ├── 📄 .dockerignore           # Ignorar en build
│   │
│   ├── 📂 engine/                 # Motor de detección
│   │   ├── 📄 detector.py         # Análisis principal
│   │   ├── 📄 models.py           # Modelos del engine
│   │   ├── 📄 normalizers.py      # Normalización de texto
│   │   ├── 📄 crypto_heuristics.py # Detección de ofuscación
│   │   └── 📄 correlator.py       # Correlación y agregación
│   │
│   └── 📂 static/                 # Dashboard web
│       ├── 📄 index.html          # Página principal
│       ├── 📄 style.css           # Estilos
│       └── 📄 app.js              # Lógica frontend
│
├── 📂 collector_telegram/         # Collector Telethon
│   ├── 📄 collector.py            # Listener MTProto
│   ├── 📄 Dockerfile              # Imagen collector
│   ├── 📄 requirements.txt        # Dependencias
│   └── 📄 .dockerignore
│
├── 📂 agents/                     # Agentes IA
│   ├── 📄 __init__.py
│   ├── 📄 base_agent.py           # Clase base OpenAI
│   ├── 📄 agent_a.py              # Psicología forense
│   ├── 📄 agent_b.py              # Threat intelligence
│   └── 📄 agent_c.py              # Estrategia y consolidación
│
├── 📂 reporting/                  # Generación de reportes
│   ├── 📄 __init__.py
│   ├── 📄 pdf_generator.py        # Generador PDF (ReportLab)
│   ├── 📄 docx_generator.py       # Generador DOCX (python-docx)
│   └── 📄 email_sender.py         # Envío SMTP
│
├── 📂 rules/                      # Reglas multi-idioma
│   ├── 📄 es.yaml                 # Español
│   ├── 📄 en.yaml                 # Inglés
│   ├── 📄 ar.yaml                 # Árabe
│   ├── 📄 ru.yaml                 # Ruso
│   ├── 📄 zh.yaml                 # Chino
│   └── 📄 ko.yaml                 # Coreano
│
├── 📂 tests/                      # Suite de tests
│   └── 📄 test_engine.py          # 20 tests del motor
│
└── 📂 data/                       # Datos generados (NO commitear)
    ├── 📄 *.pdf                   # Reportes PDF
    ├── 📄 *.docx                  # Reportes DOCX
    ├── 📄 *.session               # Sesión Telethon
    └── 📄 .gitkeep
```

---

## 🧪 Desarrollo y Tests

### Ejecutar tests

```bash
# Instalar dependencias de desarrollo
pip install pytest pytest-asyncio

# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar tests con cobertura
python -m pytest tests/ --cov=orchestrator_api --cov-report=html
```

### Tests incluidos

```
tests/test_engine.py
├── TestDetector (8 tests)
│   ├── test_high_risk_spanish
│   ├── test_low_risk_spanish
│   ├── test_high_risk_english
│   ├── test_crypto_detection
│   ├── test_euphemism_detection
│   ├── test_behavioral_markers
│   ├── test_empty_text
│   └── test_yaml_format_consistency
├── TestNormalizers (3 tests)
│   ├── test_leetspeak_basic
│   ├── test_normalize_common
│   └── test_arabic_normalization
├── TestCryptoHeuristics (3 tests)
│   ├── test_shannon_entropy
│   ├── test_base64_detection
│   └── test_crypto_signals
├── TestCorrelator (2 tests)
│   ├── test_risk_levels
│   └── test_aggregate_by_user
└── TestSchemas (4 tests)
    ├── test_message_create_valid
    ├── test_message_create_text_limit
    ├── test_case_update_valid_status
    └── test_case_update_invalid_status

Total: 20 tests
```

### Desarrollo local (sin Docker)

```bash
# Instalar dependencias
pip install -r orchestrator_api/requirements.txt

# Configurar variables de entorno
export DATABASE_URL="postgresql://user:pass@localhost:5432/osint"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="tu_secret_key"
export INTERNAL_API_KEY="tu_internal_key"
export HASH_SALT="tu_hash_salt"

# Iniciar API
uvicorn orchestrator_api.main:app --reload

# En otra terminal, iniciar worker
celery -A orchestrator_api.worker.celery_app worker --loglevel=info

# En otra terminal, iniciar beat
celery -A orchestrator_api.beat_worker.celery_app beat --loglevel=info
```

---

## 🔒 Seguridad

### Medidas implementadas

| Categoría | Medida | Estado |
|-----------|--------|:------:|
| **Autenticación** | JWT con expiración configurable (15 min default) | ✅ |
| **Autorización** | RBAC con roles (admin, analyst, viewer) | ✅ |
| **Service-to-Service** | API Key interna para collector → API | ✅ |
| **Passwords** | bcrypt hashing para usuarios | ✅ |
| **Pseudonimización** | SHA-256 + salt para usuarios Telegram | ✅ |
| **Redis** | Autenticación con password + red aislada | ✅ |
| **Docker** | Contenedores non-root (USER appuser) | ✅ |
| **Redes** | Segmentación backend/app | ✅ |
| **Secrets** | Todos obligatorios, sin fallbacks inseguros | ✅ |
| **CORS** | Orígenes configurables desde env var | ✅ |
| **Input Validation** | max_length en textos, Literal para enums | ✅ |
| **SQL Injection** | ORM SQLAlchemy en todas las queries | ✅ |
| **Prompt Injection** | Sanitización + instrucciones defensivas en agentes | ✅ |
| **Sherlock** | Fijado a tag específico (v0.14.4) | ✅ |

### Buenas prácticas

1. **Nunca commitear `.env`** - Ya está en `.gitignore`
2. **Rotar claves periódicamente** - Especialmente `SECRET_KEY` y `INTERNAL_API_KEY`
3. **Usar contraseñas fuertes** - Mínimo 12 caracteres para usuarios
4. **Limitar `MONITORED_CHATS`** - No monitorear todos los chats sin necesidad
5. **Revisar logs regularmente** - `docker compose logs -f`
6. **Actualizar dependencias** - `pip install --upgrade -r requirements.txt`

---

## 🐛 Troubleshooting

### El collector no se conecta

```bash
# Verificar credenciales de Telegram
docker compose logs collector

# Si ves "Unauthorized", regenera TG_API_ID/TG_API_HASH en my.telegram.org
```

### La API no arranca

```bash
# Verificar que todas las variables obligatorias estén en .env
docker compose logs orchestrator_api

# Errores comunes:
# - "SECRET_KEY environment variable is required" → Falta SECRET_KEY
# - "INTERNAL_API_KEY environment variable is required" → Falta INTERNAL_API_KEY
```

### Redis no conecta

```bash
# Verificar que Redis esté healthy
docker compose ps redis

# Si no está healthy, reiniciar
docker compose restart redis
```

### Los agentes IA no responden

```bash
# Verificar OPENAI_API_KEY
docker compose logs worker | grep -i openai

# Si ves "Incorrect API key", verificar en platform.openai.com
```

### El dashboard no carga

```bash
# Verificar que orchestrator_api esté corriendo
docker compose ps orchestrator_api

# Ver logs
docker compose logs orchestrator_api

# Acceder directamente a la API
curl http://localhost:8000/health
```

### Limpiar todo y empezar de nuevo

```bash
# Parar y eliminar contenedores
docker compose down

# Eliminar volúmenes (¡BORRA TODOS LOS DATOS!)
docker compose down -v

# Reconstruir desde cero
docker compose up --build -d
```

---

## 📊 Métricas y Monitoreo

### Ver logs en tiempo real

```bash
# Todos los servicios
docker compose logs -f

# Servicio específico
docker compose logs -f orchestrator_api
docker compose logs -f worker
docker compose logs -f collector
docker compose logs -f beat

# Últimas 100 líneas
docker compose logs --tail=100 worker
```

### Estadísticas del sistema

```bash
# Health check completo
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/health

# Dashboard stats
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/stats/dashboard
```

---

## 🤝 Contribuir

Este es un proyecto privado de **MuRDoK-1982**. Para reportar problemas o sugerir mejoras:

1. Abrir un issue en GitHub
2. Contactar: gustavolobatoclara@gmail.com
3. Asunto: `[PROPUESTA] - Descripción breve`

---

## 📜 Licencia

Este proyecto está bajo licencia propietaria. Ver [LICENSE](LICENSE) y [HISPANSHIELD_LICENSE.md](HISPANSHIELD_LICENSE.md).

---

## 👨‍💻 Autor

**MuRDoK-1982-**  
*Senior OSINT/CTI Architect & Python Backend Engineer*

<div align="center">

🛡️ **HISPANSHIELD — Legión de Ciberdefensa** 🛡️

*Desarrollado con dedicación para la comunidad de inteligencia*

</div>

---

<div align="center">

**¿Te fue útil este proyecto?**

[![Ko-fi](https://img.shields.io/badge/Apoya%20este%20proyecto-Ko--fi-ff5e5b?style=for-the-badge&logo=kofi)](https://ko-fi.com/murdok1982)

</div>
