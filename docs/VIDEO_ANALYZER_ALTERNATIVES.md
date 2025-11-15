# VideoAnalyzer API 替代方案 - GitHub开源工具调研

## 📋 需求确认

根据PRD，我们需要一个能够：
1. **提取视频结构**：时长、关键帧、场景分割
2. **文本转录**：视频中的语音转文字
3. **分镜表格**：生成分镜信息（shot_table）
4. **视觉元素分析**：画面内容理解

**重要发现**：VideoAnalyzer不是TrendRadar的一部分，是独立的工具。

## 🏆 推荐方案（按优先级）

### 方案A：PySceneDetect + Whisper + MoviePy（推荐）⭐⭐⭐⭐⭐

**组合优势**：
- ✅ 三个成熟稳定的Python库
- ✅ 文档完善，社区活跃
- ✅ 易于集成到现有Python项目
- ✅ 完全开源，无API限制

**工具详情**：

#### 1. PySceneDetect (`/breakthrough/pyscenedetect`)
- **功能**：场景检测、关键帧提取、视频分割
- **安装**：`pip install scenedetect[opencv]`
- **使用示例**：
```python
from scenedetect import detect, ContentDetector, split_video_ffmpeg

# 检测场景
scene_list = detect('video.mp4', ContentDetector())
# 返回: [(start_time, end_time), ...]

# 分割视频
split_video_ffmpeg('video.mp4', scene_list)
```

#### 2. Whisper (OpenAI)
- **功能**：语音转文字（支持多语言）
- **安装**：`pip install openai-whisper`
- **使用示例**：
```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("video.mp4")
transcript = result["text"]
```

#### 3. MoviePy (`/zulko/moviepy`)
- **功能**：视频处理、帧提取、时长获取
- **安装**：`pip install moviepy`
- **使用示例**：
```python
from moviepy.editor import VideoFileClip

clip = VideoFileClip("video.mp4")
duration = clip.duration  # 获取时长
frame = clip.get_frame(5.0)  # 获取第5秒的帧
```

**集成方案**：
```python
# 伪代码示例
def analyze_video(video_url):
    # 1. 下载视频（如果需要）
    video_path = download_video(video_url)
    
    # 2. 使用MoviePy获取基本信息
    clip = VideoFileClip(video_path)
    duration = clip.duration
    
    # 3. 使用PySceneDetect检测场景
    scene_list = detect(video_path, ContentDetector())
    shot_table = [
        {"start_time": s[0].get_seconds(), 
         "end_time": s[1].get_seconds()}
        for s in scene_list
    ]
    
    # 4. 使用Whisper转录音频
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    transcript = result["text"]
    
    # 5. 返回结构化数据
    return {
        "duration": duration,
        "shot_table": shot_table,
        "transcript": transcript
    }
```

---

### 方案B：video-analyzer（如果找到）⭐⭐⭐⭐

**特点**：
- 结合 Llama 11B 视觉模型和 OpenAI Whisper
- 提取关键帧、转录音频、生成视频描述
- 完全本地运行，无需云服务

**问题**：
- ⚠️ 需要确认具体的GitHub仓库
- ⚠️ 需要评估部署复杂度

**搜索建议**：
- GitHub搜索："video-analyzer llama whisper"
- 或搜索："llama video analysis whisper"

---

### 方案C：VideoPipe (`/sherlockchou86/videopipe`)⭐⭐⭐

**特点**：
- C++框架，高性能
- 插件化架构，灵活扩展
- 支持对象检测、跟踪、行为分析

**劣势**：
- C++实现，集成需要更多工作
- 主要面向实时视频流分析
- 可能过于复杂

---

### 方案D：自建服务（基于现有工具）⭐⭐⭐⭐

**技术栈**：
- **FFmpeg**：视频处理基础（下载、格式转换）
- **PySceneDetect**：场景检测
- **Whisper**：语音转录
- **OpenCV**：图像处理（关键帧提取）
- **DeepSeek LLM**：内容理解和结构化（已有）

**优势**：
- 完全可控
- 可以定制化输出格式
- 与现有系统集成度高

**实现示例**：
```python
# backend/app/utils/video_analyzer_local.py
import whisper
from scenedetect import detect, ContentDetector
from moviepy.editor import VideoFileClip
import cv2

class LocalVideoAnalyzer:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
    
    async def analyze(self, video_url: str, options: dict = None):
        # 1. 下载视频
        video_path = await self._download_video(video_url)
        
        # 2. 获取基本信息
        clip = VideoFileClip(video_path)
        duration = clip.duration
        
        # 3. 场景检测
        scene_list = detect(video_path, ContentDetector())
        shot_table = [
            {
                "start_time": s[0].get_seconds(),
                "end_time": s[1].get_seconds(),
                "description": ""  # 可以用LLM生成
            }
            for s in scene_list
        ]
        
        # 4. 语音转录
        result = self.whisper_model.transcribe(video_path)
        transcript = result["text"]
        
        # 5. 关键帧提取（可选）
        key_frames = self._extract_key_frames(video_path, scene_list)
        
        return {
            "duration": duration,
            "shot_table": shot_table,
            "transcript": transcript,
            "key_frames": key_frames
        }
```

---

## 📊 对比分析

| 方案 | 集成难度 | 功能完整性 | 性能 | 成本 | 推荐度 |
|------|---------|-----------|------|------|--------|
| PySceneDetect + Whisper + MoviePy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐⭐ |
| video-analyzer | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐ |
| VideoPipe | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 免费 | ⭐⭐⭐ |
| 自建服务 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐ |

---

## 🎯 最终推荐

### 短期方案（快速实现）
**使用方案A：PySceneDetect + Whisper + MoviePy**
- 快速集成，1-2天可完成
- 功能完整，满足所有需求
- 文档完善，易于维护

### 长期方案（优化）
**基于方案A，增加自建服务**
- 封装为独立的VideoAnalyzer服务
- 添加缓存和优化
- 支持批量处理

---

## 📝 实施步骤

### 第一步：安装依赖
```bash
pip install scenedetect[opencv] openai-whisper moviepy
```

### 第二步：创建本地VideoAnalyzer
创建 `backend/app/utils/video_analyzer_local.py`

### 第三步：修改配置
在 `backend/app/core/config.py` 中添加：
```python
VIDEO_ANALYZER_USE_LOCAL: bool = True  # 使用本地分析
VIDEO_ANALYZER_WHISPER_MODEL: str = "base"  # whisper模型大小
```

### 第四步：更新ContentStructureAgent
修改 `backend/app/agents/content_structure_agent.py`，优先使用本地分析器

### 第五步：测试
- 测试单个视频分析
- 测试批量处理
- 性能优化

---

## 🔗 相关链接

- PySceneDetect: https://github.com/breakthrough/pyscenedetect
- MoviePy: https://github.com/zulko/moviepy
- Whisper: https://github.com/openai/whisper
- VideoPipe: https://github.com/sherlockchou86/videopipe

---

## 📌 注意事项

1. **Whisper模型大小**：
   - `tiny`: 最快，准确度较低
   - `base`: 平衡（推荐）
   - `small`: 更准确，较慢
   - `medium/large`: 最准确，但很慢

2. **性能优化**：
   - 使用GPU加速Whisper（如果可用）
   - 缓存分析结果
   - 异步处理

3. **存储考虑**：
   - 视频下载需要临时存储
   - 分析结果可以缓存到数据库

4. **错误处理**：
   - 视频下载失败
   - 格式不支持
   - 分析超时
