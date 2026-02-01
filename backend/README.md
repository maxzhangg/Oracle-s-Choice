# Oracle's Choice Backend

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure

```powershell
copy .env.example .env
# Fill in GEMINI_API_KEY
```

## Start API

```powershell
uvicorn app.main:app --reload
```

## Notes
- SQLite database file: `oracle_choice.db`
- API endpoint: `POST /chat`
