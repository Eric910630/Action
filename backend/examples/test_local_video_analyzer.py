"""
本地视频分析器测试示例
"""
import asyncio
from app.utils.video_analyzer_local import LocalVideoAnalyzer
from app.utils.video_analyzer import VideoAnalyzerClient
from app.agents import get_content_structure_agent


async def test_local_analyzer():
    """测试本地分析器"""
    print("=== 测试本地视频分析器 ===")
    
    # 创建本地分析器
    analyzer = LocalVideoAnalyzer(whisper_model="tiny")  # 使用tiny模型快速测试
    
    # 测试视频URL（需要替换为实际可访问的视频）
    video_url = "https://example.com/test_video.mp4"
    
    try:
        result = await analyzer.analyze(
            video_url,
            options={
                "download_video": True,
                "extract_key_frames": False  # 不提取关键帧，减少数据量
            }
        )
        
        print(f"✅ 分析成功！")
        print(f"时长: {result.get('duration')}秒")
        print(f"场景数: {len(result.get('shot_table', []))}")
        print(f"转录文本长度: {len(result.get('transcript', ''))}")
        print(f"转录文本: {result.get('transcript', '')[:100]}...")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")


async def test_video_analyzer_client():
    """测试VideoAnalyzerClient（自动使用本地分析器）"""
    print("\n=== 测试VideoAnalyzerClient ===")
    
    # 创建客户端（自动使用本地分析器）
    client = VideoAnalyzerClient()
    
    video_url = "https://example.com/test_video.mp4"
    
    try:
        result = await client.analyze(video_url)
        print(f"✅ 分析成功！")
        print(f"使用模式: {'本地' if client.use_local else '远程'}")
        print(f"时长: {result.get('duration')}秒")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")


async def test_content_structure_agent():
    """测试ContentStructureAgent（使用本地分析器）"""
    print("\n=== 测试ContentStructureAgent ===")
    
    # 获取Agent实例
    agent = get_content_structure_agent()
    
    # 执行分析
    result = await agent.execute({
        "url": "https://example.com/test_video.mp4",
        "title": "测试视频"
    })
    
    video_structure = result.get("video_structure", {})
    print(f"✅ Agent分析成功！")
    print(f"时长: {video_structure.get('duration')}秒")
    print(f"场景数: {len(video_structure.get('scenes', []))}")
    print(f"转录文本: {video_structure.get('transcript', '')[:100]}...")


if __name__ == "__main__":
    # 运行测试
    # asyncio.run(test_local_analyzer())
    # asyncio.run(test_video_analyzer_client())
    # asyncio.run(test_content_structure_agent())
    
    print("请取消注释上面的测试函数来运行测试")
    print("注意：需要先安装依赖: pip install -r requirements.txt")

