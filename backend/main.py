from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.root import router as root_router
from routes.scenarios import router as scenarios_router
from routes.simulation import router as simulation_router

# ============================================================================
# CREATE APP FIRST
# ============================================================================
app = FastAPI(
    title="Crowd Safety Simulation API",
    description="AI-Driven Public Infrastructure Simulation Platform",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
app.include_router(scenarios_router)
app.include_router(simulation_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
