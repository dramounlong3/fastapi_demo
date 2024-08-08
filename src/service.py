from fastapi import APIRouter
from loguru import logger

router = APIRouter()

@router.get("/")
def my_service():
    logger.info("logger.info in the my service.")
    pass