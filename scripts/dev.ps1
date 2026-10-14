# Dev server for whiteboard-digitizer
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
