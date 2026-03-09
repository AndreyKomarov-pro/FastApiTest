from typing import Dict

from fastapi import APIRouter

router = APIRouter(tags=['Health'])


@router.get('/healthcheck')
async def healthcheck() -> Dict[str, str]:
    return {'status': 'ok'}