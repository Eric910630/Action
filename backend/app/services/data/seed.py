"""
初始数据种子
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.product import LiveRoom
from loguru import logger


def create_initial_live_rooms(db: Session):
    """创建初始直播间数据"""
    
    live_rooms_data = [
        {
            "name": "时尚真惠选",
            "category": "女装",
            "keywords": ["女装", "时尚", "穿搭", "连衣裙", "上衣", "裤子", "外套"],
            "ip_character": "罗永浩",
            "style": "时尚潮流"
        },
        {
            "name": "好物真惠选",
            "category": "家具",
            "keywords": ["家具", "沙发", "床", "桌子", "椅子", "柜子", "家居"],
            "ip_character": "罗永浩",
            "style": "实用耐用"
        },
        {
            "name": "生活真惠选",
            "category": "家具",
            "keywords": ["家具", "茶几", "电视柜", "餐桌", "办公桌", "书柜"],
            "ip_character": "罗永浩",
            "style": "现代简约"
        },
        {
            "name": "家居真惠选",
            "category": "家电",
            "keywords": ["家电", "电视", "冰箱", "洗衣机", "空调", "热水器", "小家电"],
            "ip_character": "罗永浩",
            "style": "科技智能"
        },
        {
            "name": "轻奢真惠选",
            "category": "奢侈品",
            "keywords": ["奢侈品", "二手", "包包", "手表", "珠宝", "名牌", "大牌"],
            "ip_character": "罗永浩",
            "style": "高端精致"
        },
        {
            "name": "美妆真惠选",
            "category": "美妆",
            "keywords": ["美妆", "化妆品", "护肤品", "口红", "粉底", "眼影", "面膜"],
            "ip_character": "罗永浩",
            "style": "美丽时尚"
        },
        {
            "name": "童装真惠选",
            "category": "童装",
            "keywords": ["童装", "儿童", "宝宝", "亲子", "童鞋", "童帽"],
            "ip_character": "罗永浩",
            "style": "温馨可爱"
        }
    ]
    
    # 旧名称到新名称的映射
    name_mapping = {
        "女装直播间": "时尚真惠选",
        "家具直播间1": "好物真惠选",
        "家具直播间2": "生活真惠选",
        "家电直播间": "家居真惠选",
        "二手奢侈品直播间": "轻奢真惠选",
        "美妆直播间": "美妆真惠选",
        "童装直播间": "童装真惠选"
    }
    
    created_count = 0
    updated_count = 0
    
    for room_data in live_rooms_data:
        # 先检查新名称是否已存在
        existing_by_new_name = db.query(LiveRoom).filter(
            LiveRoom.name == room_data["name"]
        ).first()
        
        if existing_by_new_name:
            logger.info(f"直播间 '{room_data['name']}' 已存在，跳过")
            continue
        
        # 检查是否有旧名称的直播间需要更新
        old_name = None
        for old, new in name_mapping.items():
            if new == room_data["name"]:
                old_name = old
                break
        
        if old_name:
            existing_by_old_name = db.query(LiveRoom).filter(
                LiveRoom.name == old_name,
                LiveRoom.category == room_data["category"]
            ).first()
            
            if existing_by_old_name:
                # 更新现有直播间的名称
                existing_by_old_name.name = room_data["name"]
                existing_by_old_name.keywords = room_data["keywords"]
                existing_by_old_name.ip_character = room_data["ip_character"]
                existing_by_old_name.style = room_data["style"]
                existing_by_old_name.updated_at = datetime.now()
                updated_count += 1
                logger.info(f"更新直播间: {old_name} -> {room_data['name']}")
                continue
        
        # 创建新直播间
        live_room = LiveRoom(
            id=str(uuid.uuid4()),
            name=room_data["name"],
            category=room_data["category"],
            keywords=room_data["keywords"],
            ip_character=room_data["ip_character"],
            style=room_data["style"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(live_room)
        created_count += 1
        logger.info(f"创建直播间: {room_data['name']}")
    
    db.commit()
    logger.info(f"成功创建 {created_count} 个直播间，更新 {updated_count} 个直播间")
    return created_count + updated_count


if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        create_initial_live_rooms(db)
    finally:
        db.close()

