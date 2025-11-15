# 本地视频分析器集成文档

## 📋 概述

已成功集成 PySceneDetect + Whisper + MoviePy 作为本地视频分析工具包，Agent可以直接调用。

## ✅ 已完成的工作

### 1. 依赖安装
在 `backend/requirements.txt` 中添加：
- `scenedetect[opencv]>=0.6.2` - 场景检测
- `openai-whisper>=20231117` - 语音转文字
- `moviepy>=1.0.3` - 视频处理
- `opencv-python>=4.8.0` - 图像处理

### 2. 创建本地分析器
**文件**: `backend/app/utils/video_analyzer_local.py`

**功能**：
- ✅ 视频下载（从URL）
- ✅ 视频基本信息提取（时长、分辨率、FPS）
- ✅ 场景检测（使用PySceneDetect）
- ✅ 语音转录（使用Whisper）
- ✅ 关键帧提取（可选）
- ✅ 临时文件管理

### 3. 更新VideoAnalyzerClient
**文件**: `backend/app/utils/video_analyzer.py`

**改进**：
- ✅ 支持本地和远程两种模式
- ✅ 自动降级机制（本地失败→远程API）
- ✅ 配置驱动（通过环境变量控制）

### 4. 更新配置
**文件**: `backend/app/core/config.py`

**新增配置项**：
```python
VIDEO_ANALYZER_USE_LOCAL: bool = True  # 是否使用本地分析器（默认True）
VIDEO_ANALYZER_WHISPER_MODEL: str = "base"  # Whisper模型大小
```

### 5. Agent集成
**文件**: `backend/app/agents/content_structure_agent.py`

**改进**：
- ✅ 自动使用本地分析器（如果可用）
- ✅ 支持关键帧提取
- ✅ 保持与远程API的兼容性

## 🚀 使用方法

### Agent直接调用

```python
from app.agents import get_content_structure_agent

# 获取Agent实例
agent = get_content_structure_agent()

# 执行分析
result = await agent.execute({
    "url": "https://example.com/video.mp4",
    "title": "视频标题"
})

# result包含：
# - video_structure: 视频结构信息
#   - duration: 时长
#   - scenes: 场景列表
#   - transcript: 文本转录
#   - key_frames: 关键帧（如果启用）
```

### 直接使用VideoAnalyzerClient

```python
from app.utils.video_analyzer import VideoAnalyzerClient

# 创建客户端（自动使用本地分析器）
client = VideoAnalyzerClient()

# 分析视频
result = await client.analyze(
    "https://example.com/video.mp4",
    options={
        "extract_key_frames": False,  # 是否提取关键帧
        "whisper_model": "base"  # 覆盖默认模型
    }
)
```

### 直接使用LocalVideoAnalyzer

```python
from app.utils.video_analyzer_local import LocalVideoAnalyzer

# 创建本地分析器
analyzer = LocalVideoAnalyzer(whisper_model="base")

# 分析视频
result = await analyzer.analyze(
    "https://example.com/video.mp4",
    options={
        "download_video": True,  # 是否需要下载
        "extract_key_frames": False  # 是否提取关键帧
    }
)
```

## ⚙️ 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# 使用本地分析器（默认True）
VIDEO_ANALYZER_USE_LOCAL=true

# Whisper模型大小（tiny, base, small, medium, large）
VIDEO_ANALYZER_WHISPER_MODEL=base

# 远程API（可选，作为降级方案）
VIDEO_ANALYZER_API_URL=http://your-api-url
VIDEO_ANALYZER_API_KEY=your-api-key
```

### Whisper模型选择

| 模型 | 参数量 | 速度 | 准确度 | 推荐场景 |
|------|--------|------|--------|----------|
| tiny | 39M | ⭐⭐⭐⭐⭐ | ⭐⭐ | 快速测试 |
| base | 74M | ⭐⭐⭐⭐ | ⭐⭐⭐ | **推荐** |
| small | 244M | ⭐⭐⭐ | ⭐⭐⭐⭐ | 高质量需求 |
| medium | 769M | ⭐⭐ | ⭐⭐⭐⭐⭐ | 最高质量 |
| large | 1550M | ⭐ | ⭐⭐⭐⭐⭐ | 专业场景 |

## 📊 返回数据格式

```python
{
    "duration": 120.5,  # 视频时长（秒）
    "fps": 30.0,  # 帧率
    "size": (1920, 1080),  # 分辨率
    "shot_table": [  # 场景列表
        {
            "shot_number": 1,
            "start_time": 0.0,
            "end_time": 5.2,
            "duration": 5.2,
            "start_frame": 0,
            "end_frame": 156,
            "description": ""
        },
        # ...
    ],
    "transcript": "视频的文本转录内容...",
    "script_content": "视频的文本转录内容...",  # 兼容字段
    "segments": [  # 转录分段
        {
            "start": 0.0,
            "end": 5.2,
            "text": "第一段文本"
        },
        # ...
    ],
    "language": "zh",  # 检测到的语言
    "key_frames": [],  # 关键帧（如果启用）
    "video_info": {  # 视频详细信息
        "duration": 120.5,
        "fps": 30.0,
        "size": (1920, 1080),
        "width": 1920,
        "height": 1080
    }
}
```

## 🔄 工作流程

```
ContentStructureAgent.execute()
    ↓
VideoAnalyzerClient.analyze()
    ↓
LocalVideoAnalyzer.analyze()
    ↓
1. 下载视频（如果需要）
2. 获取视频信息（MoviePy）
3. 场景检测（PySceneDetect）
4. 语音转录（Whisper）
5. 关键帧提取（可选，MoviePy）
    ↓
返回结构化数据
```

## ⚠️ 注意事项

### 1. 依赖安装

首次使用前需要安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

### 2. Whisper模型下载

首次使用Whisper时，会自动下载模型（可能需要一些时间）：
- `base` 模型约 150MB
- 下载位置：`~/.cache/whisper/`

### 3. 性能考虑

- **场景检测**：相对快速（几秒到几十秒）
- **语音转录**：取决于视频长度和模型大小
  - `base` 模型：约实时速度的 0.5-1x
  - `small` 模型：约实时速度的 0.3-0.5x
- **关键帧提取**：数据量大，默认关闭

### 4. 存储空间

- 视频下载需要临时存储空间
- 临时文件默认保存在系统临时目录
- 可以配置清理策略

### 5. 错误处理

- 本地分析器失败时，自动降级到远程API（如果配置）
- 如果都不可用，会抛出异常
- 所有错误都有详细日志

## 🧪 测试

### 单元测试

```python
# backend/tests/test_video_analyzer_local.py
import pytest
from app.utils.video_analyzer_local import LocalVideoAnalyzer

@pytest.mark.asyncio
async def test_local_analyzer():
    analyzer = LocalVideoAnalyzer(whisper_model="tiny")  # 使用小模型快速测试
    result = await analyzer.analyze("test_video.mp4")
    assert "duration" in result
    assert "shot_table" in result
    assert "transcript" in result
```

### 集成测试

```python
# backend/tests/test_content_structure_agent.py
from app.agents import get_content_structure_agent

async def test_agent_with_local_analyzer():
    agent = get_content_structure_agent()
    result = await agent.execute({
        "url": "https://example.com/video.mp4",
        "title": "测试视频"
    })
    assert result.get("video_structure") is not None
```

## 📈 性能优化建议

1. **使用GPU加速Whisper**（如果可用）：
   ```bash
   pip install openai-whisper[gpu]
   ```

2. **缓存分析结果**：
   - 相同视频URL可以缓存结果
   - 避免重复分析

3. **批量处理**：
   - 使用异步并发处理多个视频
   - 注意资源限制

4. **模型选择**：
   - 开发/测试：使用 `tiny` 或 `base`
   - 生产环境：根据需求选择 `base` 或 `small`

## 🔗 相关文档

- [PySceneDetect文档](https://github.com/breakthrough/pyscenedetect)
- [Whisper文档](https://github.com/openai/whisper)
- [MoviePy文档](https://github.com/zulko/moviepy)
- [视频分析工具推荐](./VIDEO_ANALYZER_ALTERNATIVES.md)

