from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.routes.comparison import router as comparison_router
    from backend.routes.custom import router as custom_router
    from backend.routes.root import router as root_router
    from backend.routes.simulation import router as simulation_router
    from backend.routes.venue import router as venue_router
    from backend.routes.ai_endpoints import router as ai_router  # ✅ ADD
except ImportError:
    from routes.comparison import router as comparison_router
    from routes.custom import router as custom_router
    from routes.root import router as root_router
    from routes.simulation import router as simulation_router
    from routes.venue import router as venue_router
    from routes.ai_endpoints import router as ai_router  # ✅ ADD

app = FastAPI(
    title="Crowd Safety Simulation API",
    description="AI-Driven Public Infrastructure Simulation Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
app.include_router(simulation_router)
app.include_router(venue_router)
app.include_router(comparison_router)
app.include_router(custom_router)
app.include_router(ai_router)  # ✅ ADD


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
