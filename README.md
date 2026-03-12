# LifeLog - 个人开发者专属管理台 & 灵感/产品孵化中枢

LifeLog 已从传统的记录工具，全面升级为**个人开发者专属的多项目并行管理与灵感/产品孵化中枢**。

本项目坚持“工程化、高效率、本地化”原则，去除冗余，专注于**捕捉灵感 → 深度孵化 → 知识沉淀 → 成果转化**的完整开发者闭环。

---

## 🌟 核心功能模块

### 1. 🚀 产品孵化中心 (Product Incubation)
将零散的灵感转化为完整产品的加速器：
- **阶段化向导**: 包含市场分析、技术方案、MVP 定义等标准孵化流程。
- **可视化进度**: 实时追踪项目从“点子”到“上线”的生命周期。
- **关联体系**: 自动汇聚相关任务、文档与 AI 生成的参考资料。

### 2. 👋 灵感收件箱 (Brainstorming & Inbox)
极低门槛的无压记录环境，捕获每一个技术火花：
- **即时捕获**: 支持完整 Markdown，极简录入流。
- **智能流转**:
  - `[转为任务]`: 想法成熟时直接下发至项目待办。
  - `[存入 Vault]`: 将核心知识沉淀至私人知识库。

### 3. 🧠 AI 知识流 (AI Copilot & Flow)
深度集成 **DeepSeek**，实现“任务到知识”的自动升华：
- **任务-问题转化**: 一键将已完成的任务提炼为结构化的技术难题记录。
- **AI 自动成文**: 基于任务解决过程，AI 辅助生成高质量的技术博客或复盘文章。
- **知识联动**: 打通项目与知识库，让经验不再碎片化。

### 4. ✍️ Zenith Writer (专业写作)
沉浸式、生产力级的 Markdown 编辑环境：
- **毛玻璃 UI**: 现代审美的侧边栏与浮动操作岛。
- **深度预览**: 实时渲染，支持代码高亮与复杂格式。
- **一站式发布**: 专为技术沉淀设计的排版与管理。

### 5. 📂 项目大厅 (Projects & Tasks)
告别碎片化，掌控多线并发：
- **看板墙**: 宏观掌控所有推进中的工程进度。
- **聚焦模式**: 侧贴式任务清单，深度集成项目专属备注与备忘。

---

## 🛠 技术架构

坚守“本地优先”策略，确保生产力工具的极速响应与数据安全：

### 后端 (Backend)
- **核心框架**: [FastAPI](https://fastapi.tiangolo.com/) - 异步、高性能。
- **AI 引擎**: **DeepSeek API** 深度集成（支持流式响应）。
- **数据库**: SQLite (本地存储) / 可扩展至 MySQL/PostgreSQL。
- **ORM**: SQLAlchemy 2.0。

### 前端 (Frontend)
- **现代技术栈**: [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/) + [Pinia](https://pinia.vuejs.org/)。
- **极致 UI**: 
  - [Tailwind CSS](https://tailwindcss.com/) 深度定制。
  - **Glassmorphism (毛玻璃)** 视觉增强。
  - 动态侧边栏与沉浸式暗黑模式。

---

## 🚀 快速开始

### 1. 环境准备
- Python 3.9+
- Node.js 18+

### 2. 后端部署
```bash
cd backend
# 创建并激活环境 (推荐)
python -m venv venv
./venv/Scripts/activate # Windows
# 安装依赖
pip install -r requirements.txt
# 配置环境变量 (AI Key)
cp .env.example .env 
# 启动服务
python -m uvicorn app.main:app --reload
```

### 3. 前端部署
```bash
cd frontend
npm install
npm run dev
```

### 🐳 4. Docker 部署 (推荐)
如果您希望使用容器化方案快速启动，本项目已完整适配 Docker：

```bash
# 1. 配置环境变量 (AI Key)
cp backend/.env.example backend/.env

# 2. 一键启动 (包含前端、后端与数据库卷)
docker-compose up -d --build
```

- **前端地址**: `http://localhost:8090`
- **后端 API**: `http://localhost:8091`
- **数据持久化**: 数据库文件将挂载在 Docker Volume `lifelog-data` 中，确保容器重启数据不丢失。

---

## 📂 项目结构

```text
LifeLog/
├── backend/app/          # 核心代码
│   ├── api/              # 路由 (Incubation, AI Flow, Projects...)
│   ├── crud/             # 业务逻辑中心
│   ├── models/           # 数据结构
│   └── schemas/          # Pydantic 验证模型
├── frontend/src/
│   ├── pages/            # 路由页面 (Incubation, ZenithWriter, Dashboard...)
│   └── components/       # 业务组件 (ProjectTask, ArticleFlow...)
└── docker-compose.yml    # 持久化环境部署
```

---

## ⚖️ 许可证

© 2026 LifeLog - Built for Modern Developers.