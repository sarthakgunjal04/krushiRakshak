# Backend Test Scripts

Use these scripts to verify that core backend endpoints (dashboard, advisory, Fusion Engine, chatbot) respond as expected.

---

## Prerequisites

Install dependencies:

```bash
pip install requests
```

Start the FastAPI server:

```bash
cd backend
uvicorn app.main:app --reload
```

---

## Test Scripts

### 1. Dashboard Endpoint

```bash
python test_scripts/test_dashboard.py
```

Expected output:

- Status code 200
- Weather details (temperature, humidity, rainfall, wind)
- Market prices for all crops
- Alerts list
- Crop health summary

---

### 2. Advisory Endpoint

```bash
# Test cotton advisory
python test_scripts/test_advisory.py cotton

# Test wheat advisory
python test_scripts/test_advisory.py wheat

# Test rice advisory
python test_scripts/test_advisory.py rice
```

Expected output:

- Status code 200
- Crop name, priority, and severity
- Overall analysis summary
- List of triggered rules
- Recommendations with priority levels
- Rule breakdown (pest / irrigation / market scores)
- Data sources used

---

### 3. AI Chatbot Endpoint

```bash
# Default message
python test_scripts/test_ai_chatbot.py

# Custom question
python test_scripts/test_ai_chatbot.py "What is the best time to plant rice?"

# Direct module import
python test_scripts/test_ai_chatbot.py --direct

# Multiple questions
python test_scripts/test_ai_chatbot.py --multiple
```

Prerequisites:

- `GEMINI_API_KEY` in `.env`
- Gemini SDK installed:

  ```bash
  pip install google-generativeai
  ```

Expected output:

- Status code 200
- AI-generated response from Gemini 2.5 Pro
- Friendly, easy-to-read farming advice

---

### 4. Full Suite

```bash
python test_scripts/test_all.py
```

This covers:

- Dashboard endpoint
- Cotton advisory
- Wheat advisory
- Rice advisory

---

## Example Output

✔️ **Successful Test**

```
SUCCESS: Dashboard data retrieved

Summary:
  - Total Alerts: 3
  - High Priority: 1
  - Crops Monitored: 3

Weather:
  - Temperature: 30°C
  - Humidity: 75%
  - Rainfall: 12mm
  - Wind Speed: 8 km/h
```

❌ **Failed Test**

```
ERROR: Could not connect to server.
```

Make sure the backend is running at `http://localhost:8000` using:

```bash
uvicorn app.main:app --reload
```

---

## Troubleshooting

- **Connection error**: Confirm the backend is live at `http://localhost:8000`.
- **404 error**: Ensure required data files exist under `backend/data/`.
- **500 error**: Check backend logs for JSON or file-loading issues.
- **Import error**: Run scripts from the `backend/` directory.
- **AI chatbot errors**: Confirm `GEMINI_API_KEY`, install `google-generativeai`, verify API access, and inspect logs.

---

## Notes

- All scripts use a 10-second timeout.
- The backend must be running during tests.
- Scripts print both summary and full JSON responses.
- Exit code `0` = success, `1` = failure.

