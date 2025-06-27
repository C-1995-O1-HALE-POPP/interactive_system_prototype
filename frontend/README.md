# RIS系统前端

这是RIS (Relationship Intelligence System) 系统的前端界面，提供了一个简单易用的Web界面来调用所有后端API功能。

## 功能特性

### 🎯 核心功能
- **交互处理**: 输入文本内容，自动进行情感分析、角色识别和回忆生成
- **情感分析**: 基于PAD三维情感模型进行情感分析
- **LLM服务**: 集成百炼平台DeepSeek-v3模型，提供文本生成、聊天对话等功能
- **报告生成**: 生成用户的周报告和月报告，包含情绪轨迹分析
- **多媒体识别**: 支持音频和图像文件的上传识别
- **数据管理**: 用户、角色和回忆数据的管理功能

### 🎨 界面特点
- **简洁设计**: 采用现代化的UI设计，界面简洁直观
- **标签页布局**: 6个主要功能模块，通过标签页切换
- **响应式设计**: 支持桌面和移动设备
- **实时状态**: 显示系统健康状态和LLM服务状态
- **错误处理**: 友好的错误提示和加载状态

### 📱 功能模块

#### 1. 交互处理
- 文本内容输入和处理
- 输入类型选择（话题/照片/语音）
- 实时显示处理结果
- 情感分析结果可视化
- 角色识别和回忆生成展示

#### 2. 情感分析
- PAD三维情感模型分析
- 愉悦度、唤醒度、支配度显示
- 情感标签和检测到的情感
- 情感趋势获取

#### 3. LLM服务
- LLM服务状态监控
- 支持的模型列表显示
- 文本生成功能
- 多轮聊天对话
- LLM增强情感分析

#### 4. 报告生成
- 周报告生成和展示
- 月报告生成和展示
- 情绪分布可视化
- 角色交互频率统计

#### 5. 多媒体识别
- 音频文件上传和识别
- 图像文件上传和识别
- 识别结果展示

#### 6. 数据管理
- 用户创建和管理
- 用户统计信息获取
- 角色列表查看
- 回忆列表查看

## 技术栈

- **前端框架**: React 18
- **构建工具**: Vite
- **UI组件库**: shadcn/ui
- **样式框架**: Tailwind CSS
- **图标库**: Lucide React
- **状态管理**: React Hooks
- **HTTP客户端**: Fetch API

## 快速开始

### 环境要求
- Node.js 18+
- pnpm (推荐) 或 npm

### 安装依赖
```bash
cd ris-frontend
pnpm install
```

### 开发模式
```bash
pnpm run dev
```
访问 http://localhost:5173

### 生产构建
```bash
pnpm run build
```
构建文件将生成在 `dist/` 目录

### 预览构建
```bash
pnpm run preview
```

## 配置说明

### API配置
前端默认连接到 `http://localhost:5002` 的后端服务。如需修改，请编辑 `src/lib/api.js` 文件中的 `API_BASE_URL` 常量。

```javascript
const API_BASE_URL = 'http://localhost:5002';
```

### 用户配置
默认用户ID为 `demo_user_001`，可以在界面右上角的输入框中修改。

## API调用说明

前端调用了以下后端API端点：

### 基础系统
- `GET /health` - 系统健康检查
- `GET /api/system/info` - 系统信息

### 用户管理
- `POST /api/users` - 创建用户
- `GET /api/users/{user_id}` - 获取用户信息
- `GET /api/users/{user_id}/stats` - 获取用户统计

### 交互处理
- `POST /api/interactions` - 处理交互

### 角色管理
- `GET /api/personas/{user_id}` - 获取角色列表
- `GET /api/personas/{user_id}/{persona_id}` - 获取角色详情

### 回忆管理
- `GET /api/memories/{user_id}` - 获取回忆列表
- `GET /api/memories/{user_id}/{memory_id}` - 获取回忆详情

### 情绪分析
- `POST /api/emotions/analyze` - 情感分析
- `GET /api/emotions/{user_id}/trends` - 情感趋势

### 报告生成
- `GET /api/reports/{user_id}/weekly` - 生成周报告
- `GET /api/reports/{user_id}/monthly` - 生成月报告

### 多媒体识别
- `POST /api/upload/audio` - 上传音频文件
- `POST /api/upload/image` - 上传图像文件

### LLM服务
- `GET /api/llm/status` - LLM服务状态
- `POST /api/llm/chat` - LLM聊天对话
- `POST /api/llm/generate` - LLM文本生成
- `POST /api/llm/emotion_analysis` - LLM情感分析

## 项目结构

```
ris-frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/
│   │   └── ui/            # UI组件库
│   ├── lib/
│   │   └── api.js         # API服务模块
│   ├── App.jsx            # 主应用组件
│   ├── App.css            # 样式文件
│   ├── main.jsx           # 入口文件
│   └── index.css          # 全局样式
├── dist/                  # 构建输出目录
├── package.json           # 项目配置
└── vite.config.js         # Vite配置
```

## 使用说明

### 1. 启动后端服务
确保RIS系统后端服务正在运行：
```bash
cd backend
python ris_app.py
```

### 2. 启动前端服务
```bash
cd ris-frontend
pnpm run dev
```

### 3. 访问应用
打开浏览器访问 http://localhost:5173

### 4. 基本操作流程

1. **检查系统状态**: 页面顶部显示系统健康状态和LLM服务状态
2. **设置用户ID**: 在右上角输入框中设置当前用户ID
3. **交互处理**: 在"交互处理"标签页输入文本内容，点击"处理交互"
4. **查看结果**: 系统会显示情感分析、角色识别和回忆生成结果
5. **探索其他功能**: 切换到其他标签页体验更多功能

## 部署说明

### 静态部署
构建完成后，将 `dist/` 目录部署到任何静态文件服务器即可。

### Docker部署
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 注意事项
- 确保后端服务可访问
- 配置正确的API基础URL
- 处理跨域请求（CORS）

## 开发指南

### 添加新功能
1. 在 `src/lib/api.js` 中添加新的API方法
2. 在 `App.jsx` 中创建新的组件
3. 添加到标签页或现有组件中

### 样式定制
- 修改 `src/App.css` 进行样式定制
- 使用Tailwind CSS类名进行快速样式调整
- 利用shadcn/ui组件进行一致的UI设计

### 错误处理
- API调用错误会自动显示在页面顶部
- 加载状态通过按钮禁用和加载图标显示
- 表单验证确保必要字段不为空

## 更新日志

### v1.0.0 (2025-06-26)
- ✅ 初始版本发布
- ✅ 实现所有6个功能模块
- ✅ 集成所有后端API端点
- ✅ 响应式设计和现代化UI
- ✅ 完整的错误处理和状态管理

## 技术支持

如有问题，请检查：
1. 后端服务是否正常运行
2. API基础URL配置是否正确
3. 浏览器控制台是否有错误信息
4. 网络连接是否正常

---

**RIS系统前端 - 让AI理解你的情感世界** 🤖💝

