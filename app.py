"""FastAPI entrypoint for Vercel (and local use: `uvicorn app:app --reload`).

Routes
    GET  /                      web UI (public/index.html)
    GET  /architecture          the interactive architecture page
    GET  /api/health            configuration status (no secrets)
    GET  /api/proposals         example proposals for the approval agent
    POST /api/demo              run the governed hiring demo (deterministic, no API key needed)
    POST /api/tests             run the 63-test release gate (deterministic, no API key needed)
    POST /api/review            run the approval agent on Claude (streams NDJSON progress)

Environment variables (set in Vercel → Project → Settings → Environment Variables):
    ANTHROPIC_API_KEY   required for /api/review
    CLAUDE_MODEL        optional, default claude-sonnet-5-5
"""
import json
import os
import queue
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

try:  # local development convenience; on Vercel variables come from the project settings
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from web import approval_agent, runner  # noqa: E402

ROOT = Path(__file__).resolve().parent
MAX_PROPOSAL_CHARS = 40_000

app = FastAPI(title="Governed Hiring Agent", docs_url=None, redoc_url=None)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "public" / "index.html")


@app.get("/architecture", include_in_schema=False)
def architecture():
    return FileResponse(ROOT / "architecture.html")


@app.get("/architecture-diagram.png", include_in_schema=False)
def architecture_png():
    return FileResponse(ROOT / "architecture-diagram.png")


@app.get("/api/health")
def health():
    return {
        "agent_enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
        "model": approval_agent.MODEL,
        "time_budget_seconds": approval_agent.TIME_BUDGET,
    }


@app.get("/api/proposals")
def proposals():
    return approval_agent.list_proposals()


@app.post("/api/demo")
def demo():
    return runner.run_demo()


@app.post("/api/tests")
def tests():
    return runner.run_tests()


class ReviewRequest(BaseModel):
    reviewer: str = Field(..., min_length=2, max_length=120)
    proposal_id: Optional[str] = None
    custom_text: Optional[str] = Field(None, max_length=MAX_PROPOSAL_CHARS)
    use_pilot: bool = True


@app.post("/api/review")
def review(req: ReviewRequest):
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "ANTHROPIC_API_KEY is not set.")
    if req.custom_text and req.custom_text.strip():
        text, pilot = req.custom_text, None
    elif req.proposal_id in approval_agent.PROPOSALS:
        p = approval_agent.PROPOSALS[req.proposal_id]
        text = (ROOT / p["file"]).read_text(encoding="utf-8")
        pilot = p["pilot"] if req.use_pilot else None
    else:
        raise HTTPException(400, "Choose an example proposal or paste one.")

    events: queue.Queue = queue.Queue()

    def work():
        try:
            result = approval_agent.run_approval_review(text, pilot, req.reviewer.strip(), on_event=events.put)
            events.put({"type": "result", "result": result})
        except Exception as e:  # report the failure to the browser instead of a broken stream
            events.put({"type": "error", "message": f"{type(e).__name__}: {e}"})
        finally:
            events.put(None)

    threading.Thread(target=work, daemon=True).start()

    def stream():
        while True:
            try:
                item = events.get(timeout=10)
            except queue.Empty:
                yield json.dumps({"type": "ping"}) + "\n"
                continue
            if item is None:
                break
            yield json.dumps(item, ensure_ascii=False, default=str) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
