from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.api.routes import projects, stages, configs
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)

# AI编程系统路由
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(stages.router, prefix="/stages", tags=["stages"])
api_router.include_router(configs.router, prefix="/configs", tags=["configs"])

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
