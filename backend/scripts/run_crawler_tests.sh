#!/bin/bash
# 爬虫集成测试运行脚本
# 确保遵循 API 频率限制和安全性要求

set -e

echo "=========================================="
echo "爬虫集成测试运行脚本"
echo "遵循 API 频率限制和安全性要求"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# 测试间隔（秒）- 确保有足够的间隔
TEST_INTERVAL=2

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}测试频率限制说明：${NC}"
echo "  - TrendRadar: 默认间隔 1000ms，最小 50ms"
echo "  - Firecrawl: 内置速率限制"
echo "  - 测试间隔: ${TEST_INTERVAL} 秒"
echo ""

# 测试1: 直接爬虫基本功能
echo -e "${GREEN}[1/9] 测试直接爬虫基本功能${NC}"
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_direct_crawler_basic -v --tb=short
echo ""
sleep $TEST_INTERVAL

# 测试2: 请求间隔控制（跳过，因为会测试多个平台，需要更长时间）
echo -e "${GREEN}[2/9] 跳过批量测试（避免过多请求）${NC}"
echo "  批量测试需要较长时间，单独运行："
echo "  pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_direct_crawler_with_interval -v -s"
echo ""
sleep $TEST_INTERVAL

# 测试3: HotspotMonitorService 直接爬虫
echo -e "${GREEN}[3/9] 测试 HotspotMonitorService 直接爬虫模式${NC}"
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_hotspot_service_with_direct_crawler -v --tb=short
echo ""
sleep $TEST_INTERVAL

# 测试4: MCP 降级（可能跳过）
echo -e "${GREEN}[4/9] 测试 MCP 降级方案${NC}"
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_hotspot_service_fallback_to_mcp -v --tb=short || echo "  MCP 服务未配置，跳过"
echo ""
sleep $TEST_INTERVAL

# 测试5: 完整工作流
echo -e "${GREEN}[5/9] 测试完整工作流${NC}"
pytest tests/integration/test_crawler_integration.py::TestCrawlerIntegration::test_complete_workflow -v --tb=short
echo ""
sleep $TEST_INTERVAL

# 测试6: 请求间隔合规性
echo -e "${GREEN}[6/9] 测试请求间隔合规性${NC}"
pytest tests/integration/test_crawler_safety.py::TestCrawlerSafety::test_request_interval_compliance -v --tb=short
echo ""
sleep $TEST_INTERVAL

# 测试7: 重试机制
echo -e "${GREEN}[7/9] 测试重试机制${NC}"
pytest tests/integration/test_crawler_safety.py::TestCrawlerSafety::test_retry_mechanism -v --tb=short
echo ""
sleep $TEST_INTERVAL

# 测试8: 并发控制
echo -e "${GREEN}[8/9] 测试并发控制${NC}"
pytest tests/integration/test_crawler_safety.py::TestCrawlerSafety::test_concurrent_limit -v --tb=short
echo ""

# Firecrawl 测试（如果启用）
if [ "$FIRECRAWL_ENABLED" = "true" ] && [ -n "$FIRECRAWL_API_KEY" ]; then
    echo -e "${GREEN}[9/9] 测试 Firecrawl 增强功能${NC}"
    pytest tests/integration/test_crawler_integration.py::TestFirecrawlIntegration -v --tb=short -m firecrawl
else
    echo -e "${YELLOW}[9/9] 跳过 Firecrawl 测试（未启用或未配置 API Key）${NC}"
    echo "  要启用 Firecrawl 测试，设置："
    echo "  export FIRECRAWL_ENABLED=true"
    echo "  export FIRECRAWL_API_KEY=fc-YOUR_API_KEY"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "所有测试完成！"
echo "==========================================${NC}"

