#!/usr/bin/env python3
"""
测试小红书平台是否支持
用于验证 TrendRadar API 是否支持小红书热点抓取
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.crawlers.trendradar_crawler import TrendRadarCrawler
from loguru import logger


async def test_xiaohongshu_platform():
    """测试小红书平台支持"""
    logger.info("=" * 60)
    logger.info("测试小红书平台支持")
    logger.info("=" * 60)
    
    # 创建爬虫实例
    crawler = TrendRadarCrawler()
    
    # 测试可能的平台ID
    test_platforms = [
        "xiaohongshu",  # 最可能的ID
        "xhs",  # 别名
        "redbook",  # 英文名
        "xiaohongshu-hot",  # 带hot后缀
    ]
    
    results = {}
    
    for platform in test_platforms:
        logger.info(f"\n尝试平台ID: {platform}")
        try:
            hotspots = await crawler.crawl_hotspots(platform)
            
            if hotspots:
                logger.success(f"✅ {platform} 支持！获取到 {len(hotspots)} 个热点")
                results[platform] = {
                    "supported": True,
                    "count": len(hotspots),
                    "sample": hotspots[0] if hotspots else None
                }
                # 显示前3个热点作为示例
                logger.info("前3个热点示例：")
                for i, hotspot in enumerate(hotspots[:3], 1):
                    logger.info(f"  {i}. {hotspot.get('title', 'N/A')}")
            else:
                logger.warning(f"⚠️ {platform} 返回空结果（可能不支持或当前无热点）")
                results[platform] = {
                    "supported": False,
                    "count": 0,
                    "reason": "空结果"
                }
                
        except Exception as e:
            logger.error(f"❌ {platform} 测试失败: {e}")
            results[platform] = {
                "supported": False,
                "count": 0,
                "reason": str(e)
            }
        
        # 添加间隔，避免请求过快
        await asyncio.sleep(2)
    
    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("测试结果总结")
    logger.info("=" * 60)
    
    supported_platforms = [p for p, r in results.items() if r.get("supported")]
    
    if supported_platforms:
        logger.success(f"✅ 找到支持的平台ID: {', '.join(supported_platforms)}")
        best_platform = supported_platforms[0]
        logger.info(f"\n推荐使用的平台ID: {best_platform}")
        logger.info(f"该平台获取到 {results[best_platform]['count']} 个热点")
    else:
        logger.warning("⚠️ 未找到支持的小红书平台ID")
        logger.info("\n可能的原因：")
        logger.info("1. TrendRadar API 暂不支持小红书")
        logger.info("2. 平台ID命名不同（需要查看TrendRadar文档）")
        logger.info("3. 需要特殊配置或权限")
        logger.info("\n建议：")
        logger.info("1. 查看 TrendRadar GitHub 仓库的文档")
        logger.info("2. 检查 newsnow.busiyi.world API 文档")
        logger.info("3. 联系 TrendRadar 维护者确认")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(test_xiaohongshu_platform())
        
        # 如果有支持的平台，返回成功
        if any(r.get("supported") for r in results.values()):
            sys.exit(0)
        else:
            logger.warning("未找到支持的小红书平台")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        sys.exit(1)

