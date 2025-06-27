# 交互系统后端 - 增强版

这是一个增强版的交互系统后端，支持情感分析、角色管理、多媒体识别和LLM集成。

## 新增功能

### 1. 数据库持久化存储
- 使用SQLite数据库存储角色和回忆数据
- 支持数据持久化，重启后数据不丢失
- 提供完整的数据库管理API

### 2. 音频识别功能
- 支持多种音频格式（WAV, MP3, M4A, AAC, OGG, FLAC）
- 语音转文字功能
- 支持文件上传和base64数据输入
- 自动进行情感分析和交互处理

### 3. 图片识别功能
- OCR文字识别（支持中英文）
- 图片内容分析
- 支持多种图片格式（PNG, JPG, JPEG, GIF, BMP, TIFF）
- 图片预处理优化识别准确率

### 4. LLM和多模态模型集成
- 支持OpenAI GPT模型
- 多模态内容分析（文本+图像）
- 增强情感分析
- 角色洞察生成
- 智能对话功能

### 5. 修复的图表功能
- 修复了原有的图表生成bug
- 支持情感分布饼图
- 角色交互频率柱状图
- PAD情绪趋势图
- 改进的错误处理

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置LLM服务（可选）
```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your_api_key_here"

# 可选：设置自定义API基础URL
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### 3. 启动服务
```bash
python app.py
```

服务将在 http://0.0.0.0:5000 启动

## API端点

### 基础功能
- `GET /health` - 健康检查
- `POST /analyze_emotion` - 情感分析
- `POST /process_interaction` - 完整交互处理
- `GET /get_personas` - 获取所有角色
- `GET /get_persona_memories/<persona_id>` - 获取角色回忆
- `GET /get_database_stats` - 获取数据库统计

### 多媒体识别
- `POST /recognize_audio` - 音频识别
- `POST /recognize_image` - 图片识别
- `POST /analyze_multimedia` - 综合多媒体分析

### LLM功能
- `POST /llm_chat` - LLM对话
- `POST /multimodal_analysis` - 多模态分析
- `POST /enhanced_emotion_analysis` - 增强情感分析
- `GET /persona_insights/<persona_id>` - 角色洞察
- `POST /chat_with_persona/<persona_id>` - 与角色对话
- `POST /generate_embedding` - 生成文本嵌入
- `GET /llm_service_status` - LLM服务状态

### 报告生成
- `GET /generate_weekly_report` - 生成周报告
- `GET /generate_monthly_report` - 生成月报告
- `GET /get_chart/<chart_type>/<report_type>` - 获取图表

## 使用示例

### 1. 情感分析
```bash
curl -X POST http://localhost:5000/analyze_emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "今天天气真好，心情很愉快！"}'
```

### 2. 音频识别
```bash
curl -X POST http://localhost:5000/recognize_audio \
  -F "audio=@audio_file.wav" \
  -F "language=zh-CN"
```

### 3. 图片识别
```bash
curl -X POST http://localhost:5000/recognize_image \
  -F "image=@image_file.jpg" \
  -F "language=chi_sim"
```

### 4. LLM对话（需要API密钥）
```bash
curl -X POST http://localhost:5000/llm_chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下自己"}'
```

## 数据库结构

### personas表
- id: 角色唯一标识
- name: 角色名称
- description: 角色描述
- personality_traits: 性格特征（JSON）
- communication_style: 交流风格
- created_at: 创建时间
- interaction_count: 交互次数
- emotional_tendencies: 情感倾向（JSON）
- context: 上下文信息（JSON）

### memories表
- id: 回忆唯一标识
- persona_id: 关联角色ID
- content: 回忆内容
- emotion: 情感信息（JSON）
- memory_type: 回忆类型
- timestamp: 时间戳
- entities: 实体信息（JSON）
- importance_score: 重要性分数

## 配置说明

### 环境变量
- `OPENAI_API_KEY`: OpenAI API密钥（可选）
- `OPENAI_BASE_URL`: OpenAI API基础URL（可选）

### 文件上传限制
- 最大文件大小: 50MB
- 支持的音频格式: WAV, MP3, M4A, AAC, OGG, FLAC
- 支持的图片格式: PNG, JPG, JPEG, GIF, BMP, TIFF

## 测试

运行测试脚本验证所有模块功能：
```bash
python test_modules.py
```

## 注意事项

1. LLM功能需要配置OpenAI API密钥才能使用
2. 音频识别依赖Google语音识别服务，需要网络连接
3. OCR功能需要系统安装tesseract
4. 数据库文件默认保存在当前目录下的 `interactive_system.db`
5. 图表文件保存在 `/tmp/charts` 目录下

## 故障排除

### 常见问题
1. **模块导入错误**: 确保安装了所有依赖包
2. **LLM功能不可用**: 检查API密钥配置
3. **音频识别失败**: 检查网络连接和音频格式
4. **OCR识别失败**: 确保图片清晰且包含文字
5. **数据库错误**: 检查文件权限和磁盘空间

### 日志查看
服务运行时会在控制台输出详细日志，包括：
- 模块初始化状态
- API请求处理
- 错误信息和警告

## 更新日志

### v2.0.0 (当前版本)
- ✅ 新增数据库持久化存储
- ✅ 新增音频识别功能
- ✅ 新增图片识别功能
- ✅ 集成LLM和多模态模型
- ✅ 修复图表生成bug
- ✅ 改进错误处理和日志
- ✅ 添加完整的测试套件

