"""
更新现有直播间名称的脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.product import LiveRoom
from loguru import logger

# 旧名称到新名称的映射
NAME_MAPPING = {
    "女装直播间": "时尚真惠选",
    "家具直播间1": "好物真惠选",
    "家具直播间2": "生活真惠选",
    "家电直播间": "家居真惠选",
    "二手奢侈品直播间": "轻奢真惠选",
    "美妆直播间": "美妆真惠选",
    "童装直播间": "童装真惠选"
}


def update_live_room_names(db: Session):
    """更新现有直播间的名称"""
    updated_count = 0
    
    for old_name, new_name in NAME_MAPPING.items():
        # 查找旧名称的直播间
        live_room = db.query(LiveRoom).filter(LiveRoom.name == old_name).first()
        
        if live_room:
            logger.info(f"找到直播间: {old_name} (ID: {live_room.id})")
            
            # 检查新名称是否已存在
            existing = db.query(LiveRoom).filter(
                LiveRoom.name == new_name,
                LiveRoom.id != live_room.id
            ).first()
            
            if existing:
                logger.warning(f"新名称 '{new_name}' 已存在，跳过更新 {old_name}")
                continue
            
            # 更新名称
            live_room.name = new_name
            updated_count += 1
            logger.info(f"更新直播间: {old_name} -> {new_name}")
        else:
            logger.info(f"未找到直播间: {old_name}")
    
    if updated_count > 0:
        db.commit()
        logger.info(f"成功更新 {updated_count} 个直播间名称")
    else:
        logger.info("没有需要更新的直播间")
    
    return updated_count


def main():
    """主函数"""
    db = SessionLocal()
    try:
        logger.info("开始更新直播间名称...")
        updated_count = update_live_room_names(db)
        logger.info(f"更新完成！共更新 {updated_count} 个直播间")
    except Exception as e:
        logger.error(f"更新失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

