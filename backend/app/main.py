from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    activity,
    attachments,
    auth,
    boards,
    cards,
    columns,
    comments,
    labels,
    projects,
    search,
)

app = FastAPI(
    title="Kanban API",
    version="0.1.0",
    description="Kanban board - Jira analog",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://host.docker.internal:5173",
        "http://172.17.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(cards.router)
app.include_router(search.router)
app.include_router(comments.router)
app.include_router(labels.router)
app.include_router(attachments.router)
app.include_router(activity.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
