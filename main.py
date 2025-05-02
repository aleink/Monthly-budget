from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import categories, cycles, transactions, budget, alerts

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Budget Bot is alive!"}

app.include_router(categories.router)
app.include_router(cycles.router)
app.include_router(transactions.router)
app.include_router(budget.router)
app.include_router(alerts.router)
