from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, dashboard

app = FastAPI(
    title="ParcelPilot AI Support & Operations Platform API",
    description="Multi-agent customer support and proactive operations platform with access control and source precedence resolution.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ParcelPilot AI Platform API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "users": "/api/chat/users",
            "proactive_dashboard": "/api/dashboard/proactive-issues"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
