"""BGM 曲目 API（公开，无需登录）。"""
from fastapi import APIRouter

from app.services.bgm_service import list_bgm_tracks

router = APIRouter(prefix="/api/v1/bgm", tags=["BGM"])


@router.get("/曲目")
async def list_tracks():
    tracks = list_bgm_tracks()
    available = [t for t in tracks if t.get("available")]
    return {
        "tracks": tracks,
        "availableCount": len(available),
        "hint": "将 MP3 放入 backend/static/bgm/ 后刷新页面",
    }
