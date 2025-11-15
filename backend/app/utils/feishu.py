"""
飞书客户端工具
"""
import httpx
from loguru import logger
from app.core.config import settings


class FeishuClient:
    """飞书客户端"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or settings.FEISHU_WEBHOOK_URL
    
    async def send_message(self, card_data: dict) -> dict:
        """发送飞书消息"""
        if not self.webhook_url:
            logger.warning("飞书Webhook URL未配置")
            return {"status": "error", "message": "Webhook URL未配置"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=card_data,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"发送飞书消息失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_hotspot_card(self, hotspots: list, live_room_name: str) -> dict:
        """创建热点消息卡片"""
        elements = []
        
        for idx, hotspot in enumerate(hotspots[:5], 1):  # 最多显示5个
            # 确保heat_score是整数
            heat_score = hotspot.get('heat_score', 0)
            if isinstance(heat_score, str):
                try:
                    heat_score = int(heat_score)
                except (ValueError, TypeError):
                    heat_score = 0
            elif not isinstance(heat_score, int):
                heat_score = int(heat_score) if heat_score else 0
            
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"🔥 热点{idx}：{hotspot.get('title', '')}\n热度：{'★' * (heat_score // 20)}\n视频链接：{hotspot.get('url', '')}",
                    "tag": "lark_md"
                }
            })
        
        elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "content": "查看详情",
                        "tag": "plain_text"
                    },
                    "type": "primary",
                    "url": "https://your-system.com/hotspots"
                }
            ]
        })
        
        return {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "content": f"【{live_room_name}】今日热点推荐",
                        "tag": "plain_text"
                    }
                },
                "elements": elements
            }
        }

