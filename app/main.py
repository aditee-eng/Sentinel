from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.dashboard import router

app = FastAPI(title="Sentinel API")

# allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "Sentinel is running"}