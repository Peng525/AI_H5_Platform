"""
图片素材搜索服务
支持 Unsplash / Pexels，中文关键词 → 英文翻译 → 搜索高质量配图

配置环境变量：
  UNSPLASH_ACCESS_KEY  — Unsplash API 密钥（免费申请：https://unsplash.com/developers）
  PEXELS_API_KEY       — Pexels API 密钥（免费申请：https://www.pexels.com/api/）

优先 Unsplash（图片质量更高），失败则降级 Pexels。
"""

import logging
import os
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ── 中文→英文 商务关键词词典 ──
# 积累常见词汇，持续扩充
CN_TO_EN_DICT = {
    # 行业
    "汽车": "automobile", "电动汽车": "electric vehicle", "新能源": "new energy",
    "电池": "battery", "固态电池": "solid state battery", "充电": "charging",
    "自动驾驶": "autonomous driving", "智能驾驶": "intelligent driving",
    # 科技
    "人工智能": "artificial intelligence", "AI": "AI", "大模型": "large language model",
    "芯片": "chip", "半导体": "semiconductor", "5G": "5G",
    "云计算": "cloud computing", "大数据": "big data", "物联网": "IoT",
    "机器人": "robot", "无人机": "drone",
    # 制造
    "工厂": "factory", "制造": "manufacturing", "生产线": "production line",
    "供应链": "supply chain", "物流": "logistics", "仓储": "warehouse",
    # 医疗
    "医疗": "medical", "医院": "hospital", "药物": "pharmaceutical",
    "生物技术": "biotechnology", "基因": "gene",
    # 金融
    "金融": "finance", "银行": "bank", "投资": "investment",
    "股市": "stock market", "保险": "insurance",
    # 建筑
    "建筑": "architecture", "城市": "city", "桥梁": "bridge",
    "绿色建筑": "green building", "智慧城市": "smart city",
    # 环保
    "环保": "environmental protection", "太阳能": "solar energy",
    "风能": "wind power", "碳中和": "carbon neutral",
    # 教育
    "教育": "education", "校园": "campus", "教室": "classroom",
    "在线教育": "online education",
    # 商业
    "商务": "business", "办公": "office", "会议": "meeting",
    "团队": "team", "合作": "collaboration", "握手": "handshake",
    "创新": "innovation", "创业": "startup",
    # 自然
    "自然": "nature", "风景": "landscape", "海洋": "ocean",
    "森林": "forest", "山脉": "mountain",
    # 其他
    "实验室": "laboratory", "研发": "research development",
    "数据": "data", "网络": "network", "安全": "security",
    "未来": "future", "现代化": "modern",
    "全球": "global", "世界": "world", "地图": "map",
    "流程": "process", "架构": "architecture", "系统": "system",
    "路线图": "roadmap", "时间线": "timeline",
    "背景": "background", "抽象": "abstract",
}


def _translate_cn_to_en(cn_text: str) -> str:
    """将中文关键词翻译为英文搜索词。
    策略：词典匹配 + 保留英文原词 + 去重"""
    if not cn_text or not cn_text.strip():
        return "business technology"

    # 1. 尝试词典全词匹配
    for cn, en in sorted(CN_TO_EN_DICT.items(), key=lambda x: -len(x[0])):
        if cn in cn_text:
            cn_text = cn_text.replace(cn, en)

    # 2. 提取英文单词（用户可能直接输入了英文）
    en_words = re.findall(r'[a-zA-Z]{2,}', cn_text)

    # 3. 提取中文词并尝试翻译
    cn_words = re.findall(r'[一-鿿]{2,}', cn_text)
    for w in cn_words:
        if w in CN_TO_EN_DICT:
            en_words.append(CN_TO_EN_DICT[w])

    # 4. 去重并拼接
    seen = set()
    result = []
    for w in en_words:
        wl = w.lower()
        if wl not in seen:
            seen.add(wl)
            result.append(w)

    if not result:
        # 兜底：用常见词
        result = ["business", "technology"]

    return " ".join(result[:6])


async def _search_unsplash(query: str, orientation: str = "landscape") -> Optional[str]:
    """在 Unsplash 中搜索图片，返回最相关图片的 URL。"""
    access_key = (os.environ.get("UNSPLASH_ACCESS_KEY") or "").strip()
    if not access_key:
        logger.info("Unsplash API key not configured, skip")
        return None

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": query,
                    "per_page": 5,
                    "orientation": orientation,
                },
                headers={"Authorization": f"Client-ID {access_key}"},
            )
            if resp.status_code == 403:
                logger.warning("Unsplash rate limited")
                return None
            if resp.status_code != 200:
                logger.warning("Unsplash search failed: %s %s", resp.status_code, resp.text[:200])
                return None

            data = resp.json()
            results = data.get("results") or []
            if not results:
                return None

            # 返回第一张 regular 尺寸的图片（适合 1280px 宽屏）
            return results[0]["urls"].get("regular") or results[0]["urls"].get("raw") or None

    except Exception as exc:
        logger.warning("Unsplash search error: %s", exc)
        return None


async def _search_pexels(query: str, orientation: str = "landscape") -> Optional[str]:
    """在 Pexels 中搜索图片，返回最相关图片的 URL。"""
    api_key = (os.environ.get("PEXELS_API_KEY") or "").strip()
    if not api_key:
        return None

    orient_map = {"landscape": "landscape", "portrait": "portrait", "square": "square"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.pexels.com/v1/search",
                params={
                    "query": query,
                    "per_page": 5,
                    "orientation": orient_map.get(orientation, "landscape"),
                },
                headers={"Authorization": api_key},
            )
            if resp.status_code != 200:
                logger.warning("Pexels search failed: %s", resp.text[:200])
                return None

            data = resp.json()
            photos = data.get("photos") or []
            if not photos:
                return None

            # Pexels 返回 large 尺寸
            return photos[0]["src"].get("large") or photos[0]["src"].get("original") or None

    except Exception as exc:
        logger.warning("Pexels search error: %s", exc)
        return None


async def search_image(cn_keywords: str, orientation: str = "landscape") -> Optional[str]:
    """
    根据中文关键词搜索高质量配图。

    参数:
        cn_keywords: 中文关键词（空格分隔，3-5个词），如 "电动汽车 电池 实验室"
        orientation: "landscape" | "portrait" | "square"

    返回:
        图片 URL，无结果时返回 None
    """
    if not cn_keywords or not cn_keywords.strip():
        return None

    en_query = _translate_cn_to_en(cn_keywords)
    logger.info("Image search: cn=%r → en=%r", cn_keywords[:80], en_query)

    # 优先 Unsplash（质量高）
    url = await _search_unsplash(en_query, orientation)
    if url:
        logger.info("Image found on Unsplash: %s", url[:120])
        return url

    # 降级 Pexels
    url = await _search_pexels(en_query, orientation)
    if url:
        logger.info("Image found on Pexels: %s", url[:120])
        return url

    # 都失败 → 中文原词再试一次（Pexels 部分支持中文）
    url = await _search_pexels(cn_keywords, orientation)
    if url:
        logger.info("Image found on Pexels (CN): %s", url[:120])
        return url

    logger.info("No image found for: %s", cn_keywords[:80])
    return None
