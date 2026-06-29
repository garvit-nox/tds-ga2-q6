import time, uuid
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
START_TIME = time.time()
request_counter = 0
log_store = deque(maxlen=1000)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global request_counter
        request_id = str(uuid.uuid4())
        ts = time.time()
        request_counter += 1
        response = await call_next(request)
        log_store.append({
            "level": "info",
            "ts": ts,
            "path": request.url.path,
            "request_id": request_id,
            "method": request.method,
            "status": response.status_code,
        })
        return response

app.add_middleware(ObservabilityMiddleware)

@app.get("/work")
async def work(n: int = 1):
    return {
        "email": "24f1000625@ds.study.iitm.ac.in",
        "done": n
    }

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    text = (
        "# HELP http_requests_total Total HTTP requests\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {request_counter}\n"
    )
    return PlainTextResponse(content=text)

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": round(time.time() - START_TIME, 3)}

@app.get("/logs/tail")
async def logs_tail(limit: int = 20):
    entries = list(log_store)
    return JSONResponse(content=entries[-limit:])
