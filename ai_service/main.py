from fastapi import FastAPI
from .routers import generate, polish, accept, status, intro, style, outline, regenerate

app = FastAPI(title="novel-skill AI 服务", version="0.1.0")

app.include_router(generate.router)
app.include_router(polish.router)
app.include_router(accept.router)
app.include_router(status.router)
app.include_router(intro.router)
app.include_router(style.router)
app.include_router(outline.router)
app.include_router(regenerate.router)


@app.get("/")
async def root():
    return {"message": "novel-skill AI 服务运行中"}


@app.get("/health")
async def health():
    return {"status": "ok"}