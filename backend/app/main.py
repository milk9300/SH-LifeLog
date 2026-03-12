from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.database import engine, get_db
from . import models
from .api import brainstorms, projects, tasks, events, plans, milestones, credentials, dashboard, problems, articles, incubations, graveyards, focus
from sqlalchemy import text
import traceback

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LifeLog API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8090",
        "http://127.0.0.1:8090"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册路由
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(brainstorms.router, prefix="/brainstorms", tags=["Brainstorms"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(problems.router, prefix="/problems", tags=["Problems"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(incubations.router, prefix="/incubations", tags=["Incubations"])
app.include_router(graveyards.router, prefix="/graveyards", tags=["Graveyards"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"])
app.include_router(milestones.router, prefix="/milestones", tags=["Milestones"])
# app.include_router(reflections.router, prefix="/reflections", tags=["Reflections"])
app.include_router(credentials.router, prefix="/credentials", tags=["Credentials"])
app.include_router(focus.router, prefix="/focus", tags=["Focus"])

@app.get("/")
def read_root():
    return {"message": "Welcome to LifeLog API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
