# KrushiRakshak 🌾

KrushiRakshak is a smart farming platform built to make life easier for Indian farmers.  
The goal is simple: bring **weather data, satellite readings, market prices, and expert knowledge** into one place so farmers don’t have to juggle five different apps.

---

## What is KrushiRakshak?

KrushiRakshak is a web app for farmers who want **quick, reliable updates** about their crops.  
Instead of hopping between different websites and apps, farmers can check everything in one place:

- Weather conditions  
- Crop health insights  
- Market prices  
- Personalized, actionable advisories  

The app is designed for **real rural conditions**:
- Works even when the internet is slow or drops  
- Supports multiple languages  
- Simple, no-nonsense interface  

---

## Key Features

- **Real-Time Dashboard**  
  Weather, crop status, alerts, and market prices on one screen.

- **Fusion Engine**  
  Combines weather, NDVI, market data, and crop stage before generating advisories.

- **Crop Advisories**  
  Targeted guidance for irrigation, pest control, and overall crop care.

- **Market Intelligence**  
  Tracks price momentum so farmers can time their sales better.

- **Community Forum**  
  Farmers can upload photos, ask questions, and help each other.

- **AI Chatbot**  
  Ask farming questions anytime, day or night.

- **Offline Support**  
  Uses cached data when connectivity disappears.

- **Multi-Language Support**  
  Currently English + Marathi (more coming soon).

---

## Why This System Feels Different

### Hybrid Fusion Engine
Most agri dashboards rely **only on rules** or **only on ML models**.  
KrushiRakshak uses **both**:

- Rules → keep the system explainable and predictable  
- Lightweight ML → adds confidence, context, and prioritization  

Result: alerts feel **useful**, not like random guesses.

### Built-in Community
No random WhatsApp or Telegram groups.

- Farmers post real crop issues
- Experts and peers respond in-context
- Discussions feed back into advisory logic over time

---

## Impact on the Ground

- Faster alerts by combining agronomy knowledge with real-time data  
- Farmers and experts collaborate inside the same app  
- Reduced false alerts → higher trust  

---

## System Architecture

KrushiRakshak follows a **clean 4-layer architecture**:

### Layer 1 – Farmer Web App
- React PWA  
- Offline mode (IndexedDB + Service Worker)  
- Dashboard, photo/GPS uploads, community features  

### Layer 2 – Middleware / API
- FastAPI backend  
- JWT-based authentication  
- Fusion Engine routing  
- SMS / push alerts when risk is high  

### Layer 3 – Intelligence & Analysis
- ETL jobs to keep features fresh  
- Fusion Engine blends **rules + ML**  
- Generates final advisory response  

### Layer 4 – Infrastructure & Storage
- PostgreSQL + PostGIS (core data)  
- MinIO / S3 (media storage)  
- Monitoring and admin tools  

### External Data Sources
- IMD Weather  
- Agmarknet Prices  
- Bhuvan Satellite NDVI  
- Google Gemini (AI Q&A)

Data is cached so the UI doesn’t break if an API temporarily fails.

---

## How It Works

![System Architecture Diagram](https://github.com/user-attachments/assets/d16edb5d-5c98-4622-8327-eaf0c7ee3287)

---

## Data Flow

1. Farmer opens the app  
2. Dashboard requests fresh data  
3. Backend pulls weather, market, and satellite inputs  
4. Fusion Engine processes data and applies rules  
5. Advisory is generated  
6. Backend sends results to frontend  
7. Data is cached locally for offline use  

---

## Core Components

### Fusion Engine
Analyzes weather, market, and satellite signals to detect:
- Pest risks  
- Irrigation needs  
- Price opportunities  

### Rule-Based System
Simple JSON-based rules:
- Temperature & humidity thresholds  
- Soil moisture alerts  
- Sudden price drops  

### Dashboard
Displays:
- Current weather  
- Price trends  
- Crop health  
- Alerts and advisories  

### Advisory System
Combines:
- Location  
- Crop type  
- Crop stage  
- Recent trends  

Then suggests **clear next actions**.

---

## Technology Stack

### Frontend
- React + TypeScript  
- Vite  
- Tailwind CSS  
- shadcn/ui  
- Progressive Web App (PWA)

### Backend
- FastAPI  
- SQLAlchemy  
- SQLite / PostgreSQL  
- JWT Authentication  

### External Services
- IMD Weather API  
- Agmarknet API  
- Bhuvan NDVI  
- Google Gemini  

---

## Quick Start

### Prerequisites
- Node.js 18+  
- Python 3.11+  
- Git  

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ParthChatupale/AgriSensePro.git
cd agrisense
```

### Step 2: Install Frontend Dependencies
```bash
npm install
```
### 3. Install backend dependencies
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate        # Windows
source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

### 4. Start backend
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Start frontend
```bash
npm run dev
```
### 6. Open in browser
Frontend: http://localhost:8080

Backend Docs: http://localhost:8000/docs

### Project Structure
```bash
agrisense/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── i18n/
│   ├── hooks/
│   ├── context/
│   └── lib/
├── public/
├── backend/
│   ├── app/
│   ├── data/
│   ├── rules/
│   ├── etl/
│   ├── test_scripts/
│   └── uploads/
├── docs/
├── dist/
├── dev-dist/
└── README.md

```
For backend details, see backend/README.md.

## Detailed Documentation

- `docs/Agrisense_Documentation.md`
- `backend/README.md`
- `backend/FUSION_ENGINE_SETUP.md`
- `backend/test_scripts/README.md`
- `INTEGRATION_GUIDE.md`
- `docs/DEMO_SCRIPT.md`
- `docs/dashboardscript.md`

## Development

### Running Tests

```bash
npm run test        # frontend
cd backend && pytest app/tests
```

### Production Builds

```bash
# Frontend bundle
npm run build

# Backend: deploy FastAPI using your hosting target
```

## Deployment

### Frontend
- Build with `npm run build` and deploy `dist/` to Netlify, Vercel, AWS S3/CloudFront, GitHub Pages, etc.

### Backend
- Configure environment variables (same keys as `.env`).
- Deploy FastAPI to Render, Railway, Heroku, AWS EC2, Azure App Service, etc.
- Update the frontend `config.ts` with the live backend URL.

## Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/xyz`)
3. Make changes
4. Run tests (`npm run lint`, `npm run test`)
5. Commit (`git commit -m "feat: ... "`)
6. Push (`git push origin feature/xyz`)
7. Open a PR

## License

Copyright © 2025 KrushiRakshak

## Support
