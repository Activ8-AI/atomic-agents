import uvicorn
from fastapi import FastAPI, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from custody.custodian_ledger import log_event
from telemetry.emit_heartbeat import generate_heartbeat

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/heartbeat")
def heartbeat():
    pulse = generate_heartbeat()
    log_event("HEARTBEAT_EMIT", pulse)
    return pulse

@app.post("/relay")
async def relay(request: Request):
    body = await request.json()
    envelope = body.get("envelope")
    tool = body.get("tool")

    if not envelope or not tool:
        await run_in_threadpool(log_event, "RELAY_INVALID", {"body": body})
        raise HTTPException(status_code=400, detail="Invalid envelope")

    await run_in_threadpool(log_event, "RELAY_RECEIVED", {"tool": tool, "envelope": envelope})
    return {"status": "received", "tool": tool}

if __name__ == "__main__":
    uvicorn.run("relay_server:app", host="0.0.0.0", port=8000)
