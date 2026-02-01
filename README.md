# 问象 / Oracle's Choice

SpoonOS Graph Agent 驱动的对话式占卜系统。

## 结构
- `backend/` FastAPI + SpoonOS Core Graph Agent
- `frontend/` React (中文界面)

## 快速启动

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

默认后端地址为 `http://localhost:8000`，可通过 `frontend/.env` 覆盖。
