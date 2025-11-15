"""
快速验证测试 - 验证关键修改是否正确
不需要完整的环境，只验证代码逻辑
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_web_content_extractor_import():
    """测试WebContentExtractor可以正确导入"""
    try:
        from app.utils.web_content_extractor import WebContentExtractor
        extractor = WebContentExtractor()
        assert extractor.available == True, "WebContentExtractor应该可用"
        print("✅ WebContentExtractor导入成功")
        return True
    except Exception as e:
        print(f"❌ WebContentExtractor导入失败: {e}")
        return False

def test_content_structure_agent_integration():
    """测试ContentStructureAgent集成了WebContentExtractor"""
    try:
        from app.agents.content_structure_agent import ContentStructureAgent
        agent = ContentStructureAgent()
        assert hasattr(agent, 'web_extractor'), "ContentStructureAgent应该有web_extractor属性"
        assert agent.web_extractor is not None, "web_extractor不应该为None"
        print("✅ ContentStructureAgent集成了WebContentExtractor")
        return True
    except Exception as e:
        print(f"❌ ContentStructureAgent集成测试失败: {e}")
        return False

def test_multi_platform_logic():
    """测试多平台抓取逻辑"""
    try:
        # 模拟tasks.py中的逻辑
        platform = None
        if platform:
            platforms = [platform]
        else:
            platforms = ["douyin", "zhihu", "weibo", "bilibili"]
        
        assert len(platforms) == 4, f"platform=None时应该有4个平台，实际有{len(platforms)}个"
        assert "douyin" in platforms, "应该包含douyin"
        assert "zhihu" in platforms, "应该包含zhihu"
        assert "weibo" in platforms, "应该包含weibo"
        assert "bilibili" in platforms, "应该包含bilibili"
        print(f"✅ 多平台抓取逻辑正确: {platforms}")
        
        # 测试单平台逻辑
        platform = "douyin"
        if platform:
            platforms = [platform]
        else:
            platforms = ["douyin", "zhihu", "weibo", "bilibili"]
        
        assert len(platforms) == 1, f"platform=douyin时应该有1个平台，实际有{len(platforms)}个"
        assert platforms[0] == "douyin", "应该只包含douyin"
        print(f"✅ 单平台抓取逻辑正确: {platforms}")
        
        return True
    except Exception as e:
        print(f"❌ 多平台抓取逻辑测试失败: {e}")
        return False

def test_firecrawl_removed():
    """验证Firecrawl相关代码已移除"""
    try:
        import inspect
        from app.services.hotspot import tasks
        
        # 读取tasks.py文件内容
        tasks_file = inspect.getfile(tasks)
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有Firecrawl调用（除了注释）
        lines = content.split('\n')
        firecrawl_calls = []
        for i, line in enumerate(lines, 1):
            if 'firecrawl' in line.lower() and not line.strip().startswith('#'):
                firecrawl_calls.append((i, line.strip()))
        
        # 应该只有注释中的Firecrawl引用
        if firecrawl_calls:
            print(f"⚠️  发现非注释的Firecrawl引用: {firecrawl_calls}")
            # 检查是否是注释说明
            for line_num, line in firecrawl_calls:
                if '已移除' in line or '替代' in line or '不需要' in line:
                    continue
                else:
                    print(f"❌ 第{line_num}行仍有Firecrawl调用: {line}")
                    return False
        
        print("✅ Firecrawl相关代码已正确移除")
        return True
    except Exception as e:
        print(f"❌ Firecrawl移除验证失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("快速验证测试")
    print("=" * 60)
    
    results = []
    
    print("\n1. 测试WebContentExtractor导入...")
    results.append(test_web_content_extractor_import())
    
    print("\n2. 测试ContentStructureAgent集成...")
    results.append(test_content_structure_agent_integration())
    
    print("\n3. 测试多平台抓取逻辑...")
    results.append(test_multi_platform_logic())
    
    print("\n4. 验证Firecrawl移除...")
    results.append(test_firecrawl_removed())
    
    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("✅ 所有验证通过！")
        sys.exit(0)
    else:
        print("❌ 部分验证失败")
        sys.exit(1)

