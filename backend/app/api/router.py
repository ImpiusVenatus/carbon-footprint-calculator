from fastapi import APIRouter

from app.api import activities, audit, auth, emissions, factors, reports, targets

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(factors.router)
api_router.include_router(activities.router)
api_router.include_router(emissions.router)
api_router.include_router(targets.router)
api_router.include_router(reports.router)
api_router.include_router(audit.router)
