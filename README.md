<div align="center">

```
  ██████╗ ███╗   ███╗███╗   ██╗██╗████████╗██████╗  █████╗  ██████╗███████╗
 ██╔═══██╗████╗ ████║████╗  ██║██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
 ██║   ██║██╔████╔██║██╔██╗ ██║██║   ██║   ██████╔╝███████║██║     █████╗  
 ██║   ██║██║╚██╔╝██║██║╚██╗██║██║   ██║   ██╔══██╗██╔══██║██║     ██╔══╝  
 ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║   ██║   ██║  ██║██║  ██║╚██████╗███████╗
  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝
```

### ⚡ Next-Generation Open-Source OSINT Intelligence Platform & Interactive Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React: 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](Dockerfile)
[![Zero Telemetry](https://img.shields.io/badge/OPSEC-100%25%20Private-emerald.svg)](#-opsec--privacy-first)

[English](#-english) | [Русский](#-русский)

</div>

---

## 📖 English

### Overview
**OmniTrace** is a modern, privacy-first, open-source intelligence (OSINT) platform and interactive investigation dashboard. Inspired by the convenience of *OSINT.Rocks*, OmniTrace brings complex terminal reconnaissance tools (Sherlock, Maigret, Holehe, GHunt, WHOIS, crt.sh, IP-API) into an ultra-fast, unified web application — **engineered to overcome the single-point-of-failure, OPSEC, and customization shortcomings of legacy browser OSINT tools.**

### 🚀 Why OmniTrace is 10x Better than OSINT.Rocks

| Feature | Legacy OSINT.Rocks | ⚡ OmniTrace |
| :--- | :--- | :--- |
| **Hosting & Availability** | Centralized 3rd-party SaaS (went offline / took breaks) | **100% Open-Source & Self-Hostable** via Docker or local CLI |
| **OPSEC & Privacy** | Queries logged on external servers | **Zero Telemetry**. Supports upstream Tor & SOCKS5 / HTTP proxies |
| **Input Intelligence** | Manual tab switching between tool pages | **Universal Smart Input**: Auto-detects Username, Email, Domain, IP, Phone, Hash |
| **Streaming UI** | Slow batch loading or static text dumps | **Real-Time Streaming** via Server-Sent Events (SSE) with live progress |
| **Visualization** | Plain text lists | **Interactive Relationship Link Graph** (Node & Edge visualizer) |
| **Investigation Cases** | None (ephemeral searches) | **Case Management**: Organize targets, maintain notes, track audit logs |
| **Extensibility** | Fixed external scripts | **Modular Plugin Engine**: Add custom Python modules in < 20 lines of code |
| **Forensic Export** | Basic or none | **One-click Export**: HTML Dossier (printable), JSON with SHA-256 integrity hash, CSV |

---

### 🛠 Integrated Intelligence Modules

1. **👤 Username Reconnaissance (`username_hunter`)**
   - High-concurrency asynchronous scanning across 40+ premier social, developer, gaming, video, and audio platforms (GitHub, Twitter/X, Instagram, Telegram, Reddit, Steam, TikTok, Twitch, Spotify, SoundCloud, etc.).
   - Accurate HTTP/JSON signature detection with latency measurement and error categorization.

2. **📧 Email Intelligence (`email_validator`, `holehe_presence`, `gravatar`)**
   - Domain MX record verification and temporary/disposable mailbox detection.
   - Holehe-style account presence detection (checks registrations on GitHub, Duolingo, WordPress, etc. without triggering user alerts or sending emails).
   - Gravatar identity lookup: extracts display names, avatars, bios, and linked social profiles.

3. **🌐 Network, Infrastructure & Domains (`dns_lookup`, `whois_lookup`, `crt_subdomains`, `geo_ip`)**
   - Comprehensive asynchronous DNS queries: `A`, `AAAA`, `MX`, `NS`, `TXT` (SPF/DMARC/verification), `SOA`.
   - Modern RDAP (IETF standard WHOIS replacement) for registrar details, creation and expiration dates.
   - Passive subdomain discovery via public Certificate Transparency logs (`crt.sh`).
   - IP Geolocation, ASN, ISP, and geographic coordinates via open telemetry APIs.

4. **📱 Telephony Intelligence (`phone_lookup`)**
   - Google `libphonenumber` integration for international number parsing (E.164, National, International).
   - Carrier identification, geographic region, timezones, and one-click WhatsApp/Telegram links.

5. **🔑 Breaches & Compromise (`hibp_breach`)**
   - Public breach indicators and optional HaveIBeenPwned API integration.
   - Zero-knowledge $k$-Anonymity password hash compromise checking (only sends the first 5 characters of SHA-1, target data never leaves your environment).

---

### ⚡ Quick Start

#### Option A: Docker Compose (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/kraim0v/OmniTrace.git
cd OmniTrace

# 2. Launch container
docker compose up -d

# 3. Open your browser at http://localhost:8000
```

#### Option B: Local Development Setup
```bash
# 1. Setup Backend (Python 3.12+)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py

# 2. Setup Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
# Accessible at http://localhost:5173 (proxied to backend on 8000)
```

---

## 🇷🇺 Русский

### О проекте
**OmniTrace** — это современная, ориентированная на приватность и OPSEC опенсорсная платформа для разведки по открытым источникам (OSINT) с интерактивным веб-интерфейсом.

Идея платформы вдохновлена сервисом *OSINT.Rocks*, но решает его ключевые проблемы: зависимость от сторонних серверов, риски деанонимизации расследователя и отсутствие визуального анализа связей.

### 🌟 Ключевые преимущества OmniTrace

- **🛡️ 100% OPSEC и приватность:** Ваши поисковые запросы никогда не передаются на чужие сервера. Поддержка работы через **Tor**, SOCKS5 и HTTP-прокси прямо из настроек дашборда.
- **⚡ Универсальный Smart Search:** Введите никнейм (`torvalds`), почту (`user@domain.com`), домен (`github.com`), IP (`1.1.1.1`), телефон (`+14155552671`) или хеш. Система автоматически распознает тип сущности и запустит нужные модули.
- **📡 Живой стриминг результатов (SSE):** Результаты появляются на экране мгновенно в реальном времени по мере завершения проверок, без ожидания всего скана.
- **🕸️ Интерактивный граф связей (Link Analysis):** Визуализация отношений между объектом поиска, его аккаунтами, почтами, серверами и доменами.
- **📁 Менеджер расследований (Cases):** Создавайте отдельные кейсы, прикрепляйте заметки, группируйте цели и сохраняйте историю.
- **📄 Экспорт доказательств:** Скачивание готового HTML-досье для печати, структурированного JSON с контрольной суммой SHA-256 (для фиксации цепочки доказательств) или таблицы CSV.
- **🧩 Модульная архитектура:** Легко добавлять новые модули поиска на Python.

---

### 🏗 Архитектура проекта

```
OmniTrace/
├── backend/
│   ├── app/
│   │   ├── main.py              # Точка входа FastAPI, CORS, SPA static
│   │   ├── config.py            # Настройки, прокси, таймауты
│   │   ├── core/
│   │   │   ├── detector.py      # Автоопределение сущностей (Smart Search)
│   │   │   ├── engine.py        # Асинхронный движок сканирования (SSE)
│   │   │   ├── database.py      # SQLite WAL с асинхронной блокировкой
│   │   │   ├── models.py        # Pydantic схемы данных
│   │   │   └── reporter.py      # Генератор отчетов (HTML/JSON/CSV)
│   │   └── modules/
│   │       ├── username/        # Модуль поиска по никнеймам (Sherlock-style)
│   │       ├── email/           # Валидация, Holehe-чекер, Gravatar
│   │       ├── network/         # DNS, RDAP/WHOIS, crt.sh субдомены, GeoIP
│   │       ├── phone/           # Google libphonenumber парсер
│   │       └── breaches/        # Проверка утечек (k-anonymity)
├── frontend/
│   ├── src/
│   │   ├── components/          # React компоненты (SmartSearch, GraphView, Cases, etc.)
│   │   ├── services/api.js      # REST & SSE клиент
│   │   └── App.jsx              # Главный дашборд
├── docker-compose.yml           # Запуск в 1 команду
├── Dockerfile                   # Multi-stage сборка (Frontend + Backend)
└── README.md
```

---

### 🔒 Безопасность и этичность (Disclaimer)

OmniTrace создан исключительно для специалистов по информационной безопасности, исследователей, журналистов и системных администраторов в целях защиты данных, анализа цифрового следа и законных расследований. Инструмент использует только открытые публичные протоколы и пассивные методы сбора информации.

---

### 📄 Лицензия
Распространяется под свободной лицензией [MIT](LICENSE).
Присоединяйтесь к разработке, открывайте Pull Requests и ставьте ⭐ на GitHub!
