# 产品需求文档（PRD）- 第三部分
## 技术架构与集成方案

---

## 9. 技术架构设计

### 9.1 系统架构

#### 9.1.1 整体架构
采用微服务架构，分为以下几个模块：

```
┌─────────────────────────────────────────────────────────┐
│                     前端层                               │
│  (Web管理后台 + 飞书集成)                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    API网关层                              │
│  (统一入口、鉴权、限流)                                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  热点监控服务 │  视频拆解服务 │  脚本生成服务 │  数据管理服务 │
└──────────────┴──────────────┴──────────────┴──────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   数据存储层                              │
│  (MySQL + Redis + 文件存储)                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   外部系统                                │
│  (TrendRadar + AI拆解工具 + 飞书)                        │
└─────────────────────────────────────────────────────────┘
```

#### 9.1.2 技术栈选型

**后端技术栈**：
- **语言**：Python 3.10+
- **框架**：FastAPI（API服务）
- **任务队列**：Celery + Redis（异步任务处理）
- **数据库**：MySQL 8.0（主数据库）
- **缓存**：Redis 7.0（缓存和消息队列）
- **文件存储**：本地文件系统或OSS（脚本、报告存储）

**前端技术栈**：
- **框架**：Vue 3 + TypeScript
- **UI组件**：Element Plus
- **状态管理**：Pinia
- **HTTP客户端**：Axios

**AI/ML技术栈**：
- **脚本生成**：OpenAI GPT-4 / Claude 3.5
- **文本处理**：LangChain（提示词管理）
- **向量数据库**：可选（用于相似脚本检索）

**部署技术栈**：
- **容器化**：Docker + Docker Compose
- **编排**：Kubernetes（可选，用于生产环境）
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack（可选）

---

### 9.2 模块详细设计

#### 9.2.1 热点监控服务

**职责**：
- 与TrendRadar系统集成
- 定时抓取热点数据
- 关键词筛选
- 获取视频URL和详细信息

**技术实现**：
```python
# 伪代码示例
class HotspotMonitorService:
    def __init__(self):
        self.trendradar_client = TrendRadarClient()
        self.keyword_filter = KeywordFilter()
        self.video_info_extractor = VideoInfoExtractor()
    
    async def fetch_hotspots(self, platform="douyin"):
        """抓取热点"""
        hotspots = await self.trendradar_client.get_hotspots(platform)
        return hotspots
    
    async def filter_hotspots(self, hotspots, keywords):
        """关键词筛选"""
        filtered = self.keyword_filter.filter(hotspots, keywords)
        return filtered
    
    async def get_video_info(self, video_url):
        """获取视频信息"""
        info = await self.video_info_extractor.extract(video_url)
        return info
```

**数据模型**：
```python
class Hotspot:
    id: str
    title: str
    url: str
    platform: str
    tags: List[str]
    heat_score: int
    publish_time: datetime
    video_info: VideoInfo
    match_score: float  # 匹配度
```

**API接口**：
- `GET /api/v1/hotspots` - 获取热点列表
- `POST /api/v1/hotspots/fetch` - 手动触发抓取
- `GET /api/v1/hotspots/{id}` - 获取热点详情
- `POST /api/v1/hotspots/filter` - 关键词筛选

---

#### 9.2.2 视频拆解服务

**职责**：
- 调用AI拆解工具API
- 解析拆解报告
- 提取爆款技巧
- 管理拆解报告库

**技术实现**：
```python
# 伪代码示例
class VideoAnalysisService:
    def __init__(self):
        self.analyzer_client = VideoAnalyzerClient()
        self.report_parser = ReportParser()
        self.technique_extractor = TechniqueExtractor()
    
    async def analyze_video(self, video_url):
        """调用拆解工具分析视频"""
        result = await self.analyzer_client.analyze(video_url)
        return result
    
    def parse_report(self, raw_data):
        """解析拆解报告"""
        report = self.report_parser.parse(raw_data)
        return report
    
    def extract_techniques(self, report):
        """提取爆款技巧"""
        techniques = self.technique_extractor.extract(report)
        return techniques
```

**数据模型**：
```python
class AnalysisReport:
    id: str
    video_url: str
    video_info: VideoInfo
    basic_info: BasicInfo
    shot_table: List[Shot]
    golden_3s: Golden3S
    highlights: List[Highlight]
    viral_formula: ViralFormula
    keywords: Keywords
    production_tips: ProductionTips
    created_at: datetime
```

**API接口**：
- `POST /api/v1/analysis/analyze` - 分析视频
- `GET /api/v1/analysis/reports` - 获取拆解报告列表
- `GET /api/v1/analysis/reports/{id}` - 获取拆解报告详情
- `POST /api/v1/analysis/batch` - 批量分析

---

#### 9.2.3 脚本生成服务

**职责**：
- 整合热点、商品、爆款技巧信息
- 调用AI生成脚本
- 生成分镜表格
- 提供优化建议

**技术实现**：
```python
# 伪代码示例
class ScriptGeneratorService:
    def __init__(self):
        self.llm_client = LLMClient()  # GPT-4或Claude
        self.template_manager = TemplateManager()
        self.optimizer = ScriptOptimizer()
    
    async def generate_script(self, hotspot, product, analysis_report):
        """生成脚本"""
        # 构建提示词
        prompt = self.build_prompt(hotspot, product, analysis_report)
        
        # 调用LLM生成脚本
        script_data = await self.llm_client.generate(prompt)
        
        # 解析和格式化
        script = self.parse_script(script_data)
        
        # 生成分镜表格
        shot_list = self.generate_shot_list(script)
        
        return {
            "script": script,
            "shot_list": shot_list,
            "production_notes": self.generate_notes(script),
            "tags": self.generate_tags(script)
        }
    
    def build_prompt(self, hotspot, product, analysis_report):
        """构建提示词"""
        template = self.template_manager.get_template(product.category)
        prompt = template.format(
            hotspot=hotspot,
            product=product,
            techniques=analysis_report.techniques,
            viral_formula=analysis_report.viral_formula
        )
        return prompt
```

**提示词模板示例**：
```
你是一位资深短视频编导，需要基于以下信息生成一个5-15秒的引流短视频脚本：

【热点信息】
- 热点标题：{hotspot.title}
- 热点标签：{hotspot.tags}
- 爆款技巧：{techniques}
- 爆款公式：{viral_formula}

【商品信息】
- 商品名称：{product.name}
- 品牌：{product.brand}
- 核心卖点：{product.selling_points}
- 价格：{product.price}

【要求】
1. 视频时长：5-15秒
2. 结合热点话题和商品特性
3. 运用爆款技巧和公式
4. 突出商品卖点和价格优惠
5. 适合{product.category}直播间风格

请生成：
1. 完整脚本（包含台词、动作、镜头）
2. 详细分镜表格
3. 拍摄要点
4. 剪辑要点
5. 推荐标签和话题
```

**数据模型**：
```python
class Script:
    id: str
    video_info: VideoInfo
    script_content: str
    shot_list: List[Shot]
    production_notes: ProductionNotes
    tags: Tags
    status: str  # draft/reviewed/approved
    created_at: datetime
    updated_at: datetime
```

**API接口**：
- `POST /api/v1/scripts/generate` - 生成脚本
- `GET /api/v1/scripts` - 获取脚本列表
- `GET /api/v1/scripts/{id}` - 获取脚本详情
- `PUT /api/v1/scripts/{id}` - 更新脚本
- `POST /api/v1/scripts/{id}/review` - 审核脚本
- `POST /api/v1/scripts/{id}/optimize` - 获取优化建议

---

#### 9.2.4 数据管理服务

**职责**：
- 管理商品信息
- 管理直播间信息
- 管理脚本库
- 管理拆解报告库

**数据模型**：
```python
class Product:
    id: str
    name: str
    brand: str
    category: str
    live_room_id: str
    product_link: str
    description: str
    selling_points: List[str]
    price: float
    hand_card: str
    live_date: date

class LiveRoom:
    id: str
    name: str
    category: str
    keywords: List[str]
    ip_character: str
    style: str
```

**API接口**：
- `GET /api/v1/products` - 获取商品列表
- `POST /api/v1/products` - 创建商品
- `PUT /api/v1/products/{id}` - 更新商品
- `GET /api/v1/live-rooms` - 获取直播间列表
- `POST /api/v1/live-rooms` - 创建直播间

---

### 9.3 数据库设计

#### 9.3.1 核心表结构

**hotspots表**（热点表）
```sql
CREATE TABLE hotspots (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    tags JSON,
    heat_score INT,
    publish_time DATETIME,
    video_info JSON,
    match_score FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_platform_time (platform, publish_time),
    INDEX idx_match_score (match_score)
);
```

**analysis_reports表**（拆解报告表）
```sql
CREATE TABLE analysis_reports (
    id VARCHAR(64) PRIMARY KEY,
    video_url VARCHAR(500) NOT NULL,
    video_info JSON,
    basic_info JSON,
    shot_table JSON,
    golden_3s JSON,
    highlights JSON,
    viral_formula JSON,
    keywords JSON,
    production_tips JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_video_url (video_url)
);
```

**scripts表**（脚本表）
```sql
CREATE TABLE scripts (
    id VARCHAR(64) PRIMARY KEY,
    hotspot_id VARCHAR(64),
    product_id VARCHAR(64),
    analysis_report_id VARCHAR(64),
    video_info JSON,
    script_content TEXT,
    shot_list JSON,
    production_notes JSON,
    tags JSON,
    status VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_id (product_id),
    INDEX idx_status (status)
);
```

**products表**（商品表）
```sql
CREATE TABLE products (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(50),
    live_room_id VARCHAR(64),
    product_link VARCHAR(500),
    description TEXT,
    selling_points JSON,
    price DECIMAL(10, 2),
    hand_card TEXT,
    live_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_live_room_id (live_room_id),
    INDEX idx_live_date (live_date)
);
```

**live_rooms表**（直播间表）
```sql
CREATE TABLE live_rooms (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    keywords JSON,
    ip_character VARCHAR(100),
    style VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### 9.4 外部系统集成

#### 9.4.1 TrendRadar集成

**集成方式**：
- **方案A**：API集成（如果TrendRadar提供API）
- **方案B**：数据库集成（如果TrendRadar数据存储在数据库）
- **方案C**：文件集成（如果TrendRadar输出文件）

**数据格式**：
```json
{
  "hotspots": [
    {
      "title": "热点标题",
      "url": "https://www.douyin.com/video/xxx",
      "platform": "douyin",
      "tags": ["#标签1", "#标签2"],
      "heat_score": 95,
      "publish_time": "2024-11-12 08:00:00"
    }
  ]
}
```

**集成接口**：
```python
class TrendRadarClient:
    async def get_hotspots(self, platform="douyin", date=None):
        """获取热点列表"""
        # 实现逻辑
        pass
    
    async def get_hotspot_detail(self, hotspot_id):
        """获取热点详情"""
        # 实现逻辑
        pass
```

---

#### 9.4.2 AI拆解工具集成

**集成方式**：
- **方案A**：API集成（推荐）
- **方案B**：命令行调用
- **方案C**：SDK集成

**API接口设计**（如果拆解工具提供API）：
```python
POST /api/v1/analyze
Request:
{
    "video_url": "https://www.douyin.com/video/xxx",
    "options": {
        "include_shot_table": true,
        "include_golden_3s": true,
        "include_viral_formula": true
    }
}

Response:
{
    "status": "success",
    "report_id": "report_xxx",
    "data": {
        // 拆解报告数据
    }
}
```

**集成接口**：
```python
class VideoAnalyzerClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
    
    async def analyze(self, video_url, options=None):
        """调用拆解工具分析视频"""
        response = await self.http_client.post(
            f"{self.api_url}/api/v1/analyze",
            json={
                "video_url": video_url,
                "options": options or {}
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
```

---

#### 9.4.3 飞书集成

**集成方式**：
- 使用飞书开放平台API
- Webhook推送消息

**消息卡片格式**：
```json
{
    "msg_type": "interactive",
    "card": {
        "config": {
            "wide_screen_mode": true
        },
        "header": {
            "title": {
                "content": "【女装直播间】今日热点推荐",
                "tag": "plain_text"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": "🔥 热点1：变装秀挑战\n热度：★★★★★\n视频链接：https://www.douyin.com/video/xxx",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "content": "一键拆解",
                            "tag": "plain_text"
                        },
                        "type": "primary",
                        "url": "https://your-system.com/analyze?video_url=xxx"
                    }
                ]
            }
        ]
    }
}
```

**集成接口**：
```python
class FeishuClient:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    async def send_message(self, card_data):
        """发送飞书消息"""
        response = await self.http_client.post(
            self.webhook_url,
            json=card_data
        )
        return response.json()
```

---

### 9.5 任务调度设计

#### 9.5.1 定时任务

使用Celery + Redis实现定时任务：

**任务1：每日热点抓取**
```python
@celery_app.task
def fetch_daily_hotspots():
    """每日8:00自动抓取热点"""
    monitor_service = HotspotMonitorService()
    hotspots = await monitor_service.fetch_hotspots()
    # 处理热点数据
    pass
```

**任务2：热点推送**
```python
@celery_app.task
def push_hotspots_to_feishu():
    """每日9:00推送热点到飞书"""
    # 获取筛选后的热点
    # 生成飞书消息卡片
    # 推送到飞书
    pass
```

**任务3：数据清理**
```python
@celery_app.task
def cleanup_old_data():
    """清理7天前的热点数据"""
    # 删除过期数据
    pass
```

#### 9.5.2 异步任务

**任务1：视频拆解**
```python
@celery_app.task
def analyze_video_async(video_url):
    """异步拆解视频"""
    analysis_service = VideoAnalysisService()
    report = await analysis_service.analyze_video(video_url)
    # 保存报告
    pass
```

**任务2：脚本生成**
```python
@celery_app.task
def generate_script_async(hotspot_id, product_id, analysis_report_id):
    """异步生成脚本"""
    script_service = ScriptGeneratorService()
    script = await script_service.generate_script(...)
    # 保存脚本
    pass
```

---

### 9.6 安全设计

#### 9.6.1 认证授权
- 使用JWT Token进行API认证
- 基于角色的访问控制（RBAC）
- 不同角色有不同的权限

#### 9.6.2 数据安全
- 敏感数据加密存储（商品信息、脚本数据）
- API接口使用HTTPS
- 数据库连接加密

#### 9.6.3 日志审计
- 记录所有关键操作
- 记录API调用日志
- 记录错误日志

---

*本文档为PRD第三部分，包含技术架构和集成方案。*

