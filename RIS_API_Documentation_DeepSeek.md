# RIS系统API文档 - 百炼平台DeepSeek集成版

## 系统概述

RIS (Relationship Intelligence System) 系统是一个智能关系管理系统，现已集成百炼平台的DeepSeek-v3模型，提供更强大的AI能力。

### 核心功能
- **多模态数据采集**: 支持文本、音频、图像输入
- **PAD情感分析**: 基于Pleasure-Arousal-Dominance三维情感模型
- **智能角色管理**: 自动识别和管理交互角色
- **回忆档案系统**: 持久化存储和智能分类
- **情绪轨迹报告**: 可视化情感变化趋势
- **百炼平台DeepSeek集成**: 提供强大的LLM和推理能力

### 技术架构
- **后端**: Flask + SQLite/MongoDB
- **AI模型**: 百炼平台DeepSeek-v3/R1系列
- **数据存储**: NoSQL文档数据库
- **API设计**: RESTful风格

## 百炼平台DeepSeek集成

### 支持的模型
- **deepseek-v3**: MoE模型，671B参数，激活37B
- **deepseek-r1**: 推理增强模型，支持思考过程
- **deepseek-r1-0528**: R1升级版，推理能力更强

### 配置要求
```bash
# 设置百炼平台API密钥
export DASHSCOPE_API_KEY="your_api_key_here"
```

## API端点详细说明

### 基础系统端点

#### 1. 健康检查
```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-25T03:19:28.571812",
  "system_info": {
    "database_connected": true,
    "modules_loaded": [
      "RISDataModel",
      "PADEmotionAnalyzer",
      "EnhancedMultimediaRecognizer",
      "EnhancedPersonaSync",
      "EmotionReportGenerator",
      "BailianDeepSeekService"
    ],
    "llm_service_status": {
      "service_name": "百炼平台DeepSeek服务",
      "is_available": false,
      "api_key_configured": false,
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "supported_models": ["deepseek-r1", "deepseek-r1-0528", "deepseek-v3"],
      "default_model": "deepseek-v3",
      "capabilities": [
        "文本生成",
        "多轮对话",
        "情感分析",
        "角色洞察",
        "多模态分析",
        "推理增强（R1模型）"
      ]
    }
  }
}
```

#### 2. 系统信息
```http
GET /api/system/info
```

**响应示例**:
```json
{
  "success": true,
  "system_info": {
    "name": "RIS系统",
    "version": "2.0.0",
    "description": "智能关系管理系统 - 百炼平台DeepSeek集成版",
    "api_endpoints": [
      "用户管理",
      "交互处理",
      "角色管理",
      "回忆管理",
      "情绪分析",
      "报告生成",
      "多媒体识别",
      "百炼平台LLM服务"
    ]
  }
}
```

### 用户管理端点

#### 3. 创建用户
```http
POST /api/users
Content-Type: application/json

{
  "user_id": "demo_user_001"
}
```

#### 4. 获取用户信息
```http
GET /api/users/{user_id}
```

#### 5. 获取用户统计
```http
GET /api/users/{user_id}/stats
```

### 交互处理端点

#### 6. 处理交互
```http
POST /api/interactions
Content-Type: application/json

{
  "user_id": "demo_user_001",
  "text": "今天和张三一起去北京出差，心情很好！",
  "input_type": "topic",
  "context": {
    "location": "北京",
    "time": "2025-06-25"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "interaction_id": "int_20250625_001",
    "emotion_analysis": {
      "pad_values": {
        "pleasure": 0.8,
        "arousal": 0.6,
        "dominance": 0.7
      },
      "emotion_label": "positive",
      "detected_emotions": ["开心", "兴奋"]
    },
    "personas_created": [
      {
        "persona_id": "persona_张三一",
        "name": "张三一",
        "relationship": "colleague"
      }
    ],
    "memories_created": [
      {
        "memory_id": "mem_20250625_001",
        "content": "和张三一一起去北京出差",
        "emotion_annotation": "positive"
      }
    ]
  }
}
```

### 百炼平台LLM服务端点

#### 7. LLM服务状态
```http
GET /api/llm/status
```

**响应示例**:
```json
{
  "success": true,
  "status": {
    "service_name": "百炼平台DeepSeek服务",
    "is_available": true,
    "api_key_configured": true,
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "supported_models": ["deepseek-r1", "deepseek-r1-0528", "deepseek-v3"],
    "default_model": "deepseek-v3",
    "capabilities": [
      "文本生成",
      "多轮对话",
      "情感分析",
      "角色洞察",
      "多模态分析",
      "推理增强（R1模型）"
    ]
  }
}
```

#### 8. LLM聊天对话
```http
POST /api/llm/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "你好，请介绍一下DeepSeek模型的特点"}
  ],
  "model": "deepseek-v3",
  "max_tokens": 2048,
  "temperature": 0.7
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "content": "DeepSeek-v3是一个强大的MoE（混合专家）模型...",
    "model": "deepseek-v3",
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 200,
      "total_tokens": 215
    },
    "timestamp": "2025-06-25T03:20:00.000000"
  }
}
```

#### 9. LLM文本生成
```http
POST /api/llm/generate
Content-Type: application/json

{
  "prompt": "请写一首关于人工智能的诗",
  "model": "deepseek-v3",
  "max_tokens": 1024,
  "temperature": 0.8
}
```

#### 10. LLM增强情感分析
```http
POST /api/llm/emotion_analysis
Content-Type: application/json

{
  "text": "今天工作压力很大，但是完成了重要项目，感觉很有成就感",
  "context": {
    "user_id": "demo_user_001",
    "time": "2025-06-25"
  },
  "model": "deepseek-v3"
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "pad_values": {
      "pleasure": 0.6,
      "arousal": 0.7,
      "dominance": 0.8
    },
    "emotion_category": {
      "emotion": "accomplished",
      "label": "positive",
      "intensity": 0.7
    },
    "analysis_reasoning": "文本表达了工作压力和成就感的复合情绪...",
    "detected_emotions": ["压力", "成就感", "满足"],
    "confidence": 0.85,
    "analysis_method": "llm_enhanced",
    "model_used": "deepseek-v3"
  }
}
```

#### 11. LLM角色洞察生成
```http
GET /api/llm/persona_insights/{user_id}/{persona_id}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "personality_analysis": "张三一表现出积极主动的工作态度...",
    "emotional_patterns": ["工作导向", "团队合作", "目标明确"],
    "interaction_style": "专业、友好、高效",
    "relationship_trends": "关系稳定发展，合作愉快",
    "interaction_suggestions": [
      "继续保持专业合作关系",
      "可以分享更多工作经验",
      "适当增加非工作话题交流"
    ],
    "insights_summary": "张三一是一个可靠的工作伙伴...",
    "analysis_method": "llm_insights",
    "model_used": "deepseek-v3"
  }
}
```

#### 12. 与角色进行LLM对话
```http
POST /api/llm/chat_with_persona/{user_id}/{persona_id}
Content-Type: application/json

{
  "message": "最近工作怎么样？",
  "conversation_history": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！很高兴见到你"}
  ],
  "model": "deepseek-v3"
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "persona_reply": "最近工作挺忙的，不过项目进展顺利。你那边怎么样？",
    "persona_id": "persona_张三一",
    "persona_name": "张三一",
    "model_used": "deepseek-v3",
    "timestamp": "2025-06-25T03:20:00.000000",
    "conversation_context": 4
  }
}
```

#### 13. LLM多模态内容分析
```http
POST /api/llm/multimodal_analysis
Content-Type: application/json

{
  "text": "今天拍了一张美丽的风景照",
  "image_description": "一张山水风景照，阳光明媚，湖水清澈",
  "audio_transcript": "哇，这里的风景真是太美了！",
  "context": {
    "location": "黄山",
    "weather": "晴朗"
  },
  "model": "deepseek-v3"
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "overall_sentiment": {
      "emotion": "positive",
      "confidence": 0.9
    },
    "key_themes": ["自然美景", "旅行体验", "情感表达"],
    "modality_consistency": "文本、图像和音频内容高度一致，都表达了对美景的赞美",
    "emotional_intensity": 0.8,
    "response_suggestions": [
      "询问更多旅行细节",
      "分享类似的美景体验",
      "建议其他风景名胜"
    ],
    "analysis_summary": "用户通过多种方式表达了对自然美景的喜爱...",
    "analysis_method": "multimodal_llm",
    "modalities_used": ["text", "image", "audio"]
  }
}
```

### 角色管理端点

#### 14. 获取用户角色列表
```http
GET /api/personas/{user_id}
```

#### 15. 获取角色详情
```http
GET /api/personas/{user_id}/{persona_id}
```

#### 16. 更新角色信息
```http
PUT /api/personas/{user_id}/{persona_id}
Content-Type: application/json

{
  "description": "更新的角色描述",
  "personality_traits": ["友好", "专业", "可靠"],
  "communication_style": "正式而友好"
}
```

### 回忆管理端点

#### 17. 获取回忆列表
```http
GET /api/memories/{user_id}?limit=20&emotion_filter=positive
```

#### 18. 获取回忆详情
```http
GET /api/memories/{user_id}/{memory_id}
```

#### 19. 更新回忆标注
```http
PUT /api/memories/{user_id}/{memory_id}
Content-Type: application/json

{
  "emotion_annotation": "positive",
  "tags": ["工作", "成就", "团队合作"],
  "notes": "重要的项目里程碑"
}
```

### 情绪分析端点

#### 20. PAD情感分析
```http
POST /api/emotions/analyze
Content-Type: application/json

{
  "text": "今天心情不错，完成了很多工作",
  "context": {
    "user_id": "demo_user_001",
    "timestamp": "2025-06-25T10:00:00"
  }
}
```

#### 21. 情感趋势分析
```http
GET /api/emotions/{user_id}/trends?period=week
```

### 报告生成端点

#### 22. 生成周报告
```http
GET /api/reports/{user_id}/weekly
```

**响应示例**:
```json
{
  "success": true,
  "report": {
    "period": "2025-06-18 to 2025-06-25",
    "summary": {
      "total_interactions": 15,
      "average_mood": {
        "pleasure": 0.65,
        "arousal": 0.55,
        "dominance": 0.70
      },
      "dominant_emotion": "positive"
    },
    "emotion_distribution": {
      "positive": 60,
      "negative": 25,
      "neutral": 15
    },
    "persona_interactions": {
      "张三一": 8,
      "李四": 4,
      "王五": 3
    },
    "memory_categories": {
      "工作": 40,
      "生活": 35,
      "学习": 25
    },
    "charts": {
      "emotion_trend": "/tmp/emotion_trend_chart.png",
      "persona_frequency": "/tmp/persona_frequency_chart.png"
    }
  }
}
```

#### 23. 生成月报告
```http
GET /api/reports/{user_id}/monthly
```

#### 24. 下载报告图表
```http
GET /api/reports/{user_id}/charts/{chart_type}
```

### 多媒体识别端点

#### 25. 音频识别
```http
POST /api/multimedia/recognize_audio
Content-Type: multipart/form-data

audio: [音频文件]
language: zh-CN
```

#### 26. 图像识别
```http
POST /api/multimedia/recognize_image
Content-Type: multipart/form-data

image: [图像文件]
language: chi_sim
```

#### 27. 综合多媒体分析
```http
POST /api/multimedia/analyze
Content-Type: application/json

{
  "audio_data": "base64编码的音频数据",
  "image_data": "base64编码的图像数据",
  "text": "相关文本内容",
  "user_id": "demo_user_001"
}
```

### 文件上传端点

#### 28. 上传音频文件
```http
POST /api/upload/audio
Content-Type: multipart/form-data

audio: [音频文件]
language: zh-CN
```

#### 29. 上传图像文件
```http
POST /api/upload/image
Content-Type: multipart/form-data

image: [图像文件]
language: chi_sim
```

## 错误处理

### 标准错误响应格式
```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-06-25T03:20:00.000000"
}
```

### 常见错误码
- `400`: 请求参数错误
- `401`: 未授权访问
- `404`: 资源不存在
- `500`: 服务器内部错误
- `503`: 服务不可用（如LLM服务未配置）

## 使用示例

### Python客户端示例

```python
import requests
import json

# 基础配置
BASE_URL = "http://localhost:5002"
headers = {"Content-Type": "application/json"}

# 1. 检查系统健康状态
response = requests.get(f"{BASE_URL}/health")
print("系统状态:", response.json())

# 2. 创建用户
user_data = {"user_id": "test_user_001"}
response = requests.post(f"{BASE_URL}/api/users", 
                        json=user_data, headers=headers)
print("用户创建:", response.json())

# 3. 处理交互
interaction_data = {
    "user_id": "test_user_001",
    "text": "今天和朋友小明一起看电影，很开心！",
    "input_type": "topic"
}
response = requests.post(f"{BASE_URL}/api/interactions", 
                        json=interaction_data, headers=headers)
print("交互处理:", response.json())

# 4. LLM聊天（需要配置API密钥）
chat_data = {
    "messages": [
        {"role": "user", "content": "请分析一下'今天心情很好'这句话的情感"}
    ],
    "model": "deepseek-v3"
}
response = requests.post(f"{BASE_URL}/api/llm/chat", 
                        json=chat_data, headers=headers)
print("LLM聊天:", response.json())

# 5. 生成周报告
response = requests.get(f"{BASE_URL}/api/reports/test_user_001/weekly")
print("周报告:", response.json())
```

### JavaScript客户端示例

```javascript
const BASE_URL = 'http://localhost:5002';

// 处理交互
async function processInteraction(userId, text) {
    const response = await fetch(`${BASE_URL}/api/interactions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            text: text,
            input_type: 'topic'
        })
    });
    
    const result = await response.json();
    console.log('交互处理结果:', result);
    return result;
}

// LLM情感分析
async function analyzeMoodWithLLM(text) {
    const response = await fetch(`${BASE_URL}/api/llm/emotion_analysis`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            model: 'deepseek-v3'
        })
    });
    
    const result = await response.json();
    console.log('LLM情感分析:', result);
    return result;
}

// 使用示例
processInteraction('demo_user', '今天工作很顺利，心情不错！');
analyzeMoodWithLLM('虽然遇到了困难，但最终解决了问题，很有成就感');
```

## 部署说明

### 环境要求
- Python 3.8+
- Flask 3.0+
- SQLite 3.0+
- 百炼平台API密钥

### 安装步骤

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
export DASHSCOPE_API_KEY="your_bailian_api_key"
```

3. **启动服务**
```bash
python ris_app.py
```

4. **验证部署**
```bash
curl http://localhost:5000/health
```

### 生产环境配置

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 ris_app:app

# 使用Docker部署
docker build -t ris-system .
docker run -p 5000:5000 -e DASHSCOPE_API_KEY=your_key ris-system
```

## 更新日志

### v2.0.0 (2025-06-25)
- ✅ 集成百炼平台DeepSeek-v3/R1模型
- ✅ 新增LLM增强情感分析
- ✅ 新增角色洞察生成功能
- ✅ 新增多模态内容分析
- ✅ 新增与角色的智能对话
- ✅ 优化API响应格式
- ✅ 完善错误处理机制

### v1.0.0 (2025-06-24)
- ✅ 基础RIS系统功能
- ✅ PAD情感分析
- ✅ 角色和回忆管理
- ✅ 多媒体识别
- ✅ 报告生成

## 技术支持

如有问题，请联系开发团队或查看：
- 系统健康检查: `/health`
- API状态检查: `/api/system/info`
- LLM服务状态: `/api/llm/status`

---

**RIS系统 - 智能关系管理，让AI理解你的情感世界** 🤖💝

