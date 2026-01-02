from fastapi import APIRouter
from app.api.v1 import auth, catalogues, admin, menu, config, jobs, dashboard, capacity_firewall_report, capacity_network_report
from app.api.v1.network.ipam import api as ipam
from app.api.v1.linux.morning_checklist import api as morning_checklist

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(catalogues.router)
api_router.include_router(admin.router)
api_router.include_router(menu.router)
api_router.include_router(config.router)
api_router.include_router(jobs.router)
api_router.include_router(dashboard.router)
api_router.include_router(capacity_firewall_report.router)
api_router.include_router(capacity_network_report.router)
api_router.include_router(morning_checklist.router)
api_router.include_router(ipam.router, prefix="/network/ipam", tags=["network/ipam"])

