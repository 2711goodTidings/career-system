# 计算机专业智能职业规划系统

一个面向计算机专业大学生的智能职业规划 Web 系统。系统通过个人资料、能力评估、职业路径匹配和 AI 规划建议，帮助学生了解自身能力画像，选择就业、考研、考公、留学等发展路线，并生成阶段化成长计划。

当前仓库已经完成前后端分离的主要业务闭环，属于可本地运行、可联调演示的开发版本。

## 技术栈

### 前端

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios / Fetch
- ECharts

### 后端

- FastAPI
- SQLAlchemy
- Pydantic
- MySQL
- PyMySQL
- python-dotenv
- Uvicorn

### AI 能力

- 统一由 `backend/llm_client.py` 调用外部大模型服务
- 支持 MiMo / OpenAI Chat Completions 风格接口配置
- 能力评估建议、规划问答、年度规划书依赖后端 `.env` 中的 AI 配置

## 已实现功能

### 1. 用户与登录

- 用户注册
- 用户登录
- 前端基于 Pinia 和 localStorage 保存登录状态
- 登录后解锁个人信息、能力评估、职业规划、成长规划等模块

说明：当前认证仍是开发版本，密码未做哈希加密，也没有完整 JWT 鉴权流程，生产环境需要继续加固。

### 2. 个人信息管理

- 查询、创建、修改个人资料
- 维护姓名、性别、年龄、电话、邮箱、学校、专业、年级、简介等基础信息
- 维护兴趣方向、已有技能、目标倾向、职业目标等规划字段
- 支持头像上传，并通过 `/uploads` 静态资源路径访问
- 前端提供资料完成度展示和书页式交互界面

### 3. 能力评估

- 支持两类评估：
  - 综合能力评估：逻辑思维、创新能力、沟通协作、学习能力、抗压能力、领导力
  - 计算机能力评估：编程能力、数据结构与算法、计算机基础、软件工程、后端、前端、数据库、网络、AI 与机器学习、运维部署
- 后端启动时自动初始化评估题目
- 支持提交答案、计算维度得分、生成整体等级
- 支持雷达图展示评估结果
- 支持评估历史记录查询
- 支持本地缓存相同答案对应的历史 AI 建议
- 前端支持答题进度、自动保存、清除答案、提交进度提示

### 4. 职业路径与职业推荐

- 后端内置默认职业库，并在启动时自动写入或更新
- 支持就业、考研、考公、留学四类发展路径评分
- 支持根据个人资料、能力评估和补充规划信息生成推荐路径
- 支持推荐 3 个职业或发展方向
- 推荐结果包含：
  - 路径结论
  - 路径评分
  - 个人画像
  - 计算机能力画像
  - 综合能力辅助评分
  - 推荐职业
  - 匹配度
  - 推荐理由
  - 技能差距
  - 发展建议
- 前端支持补充 GPA、排名、四六级、项目、实习、城市、经济约束、价值偏好等规划信息并重新生成

### 5. AI 成长规划

- 支持规划问答，结合用户资料、能力评估、职业推荐结果回答职业规划问题
- 支持快捷问题，例如就业/考研选择、后端准备、项目补强、算法薄弱等
- 支持年度成长规划书生成
- 年度规划会根据当前年级生成剩余学年的阶段安排
- 支持选择路径侧重：就业、考研、考公、留学
- 年度规划结果会写入数据库缓存，重复输入可复用历史结果
- 当前 AI 服务失败时，规划问答和年度规划支持本地规则兜底回复
- 前端支持导出年度规划为 PDF

## 当前开发进度

### 已完成

- 前端基础工程和主页面路由
- 后端 FastAPI 应用入口和路由拆分
- MySQL 数据模型和自动建表
- 用户注册 / 登录
- 个人资料 CRUD
- 头像上传和静态资源访问
- 综合能力评估
- 计算机能力评估
- 评估题库初始化
- 评估记录保存和历史查询
- 默认职业库初始化
- 职业路径评分
- 职业推荐报告
- AI 评估建议调用
- AI 规划问答
- AI 年度成长规划生成
- 年度规划缓存
- 前后端主要页面联调

### 待完善

- 密码加密、JWT 鉴权、权限校验等安全能力
- 数据库迁移机制，目前主要依赖 `Base.metadata.create_all`
- 自动化测试和接口测试覆盖
- 后台管理功能，例如职业库、题库、用户数据管理
- 生产环境配置、部署脚本、日志和监控
- 上传文件清理和对象存储接入
- 前端 API 地址统一环境变量化，目前部分页面仍硬编码 `http://127.0.0.1:8000`
- README 之外的后端代码注释存在历史编码问题，后续可统一清理

## 项目结构

```text
Career/
├─ frontend/
│  ├─ public/
│  ├─ src/
│  │  ├─ api/              # 前端接口封装
│  │  ├─ assets/           # 页面图片和样式资源
│  │  ├─ components/       # 公共组件
│  │  ├─ router/           # Vue Router 配置
│  │  ├─ stores/           # Pinia 状态
│  │  ├─ utils/            # Axios 实例等工具
│  │  └─ views/            # 页面组件
│  ├─ package.json
│  └─ vite.config.js
│
├─ backend/
│  ├─ routers/
│  │  ├─ auth.py           # 注册 / 登录
│  │  ├─ profile.py        # 个人资料和头像上传
│  │  ├─ assessment.py     # 能力评估
│  │  ├─ career.py         # 职业库和推荐
│  │  ├─ career_path.py    # 路径记录 CRUD
│  │  └─ planning_ai.py    # AI 规划问答和年度规划
│  ├─ uploads/avatars/     # 本地头像上传目录
│  ├─ database.py          # 数据库连接
│  ├─ dependencies.py
│  ├─ llm_client.py        # 统一 AI 调用入口
│  ├─ main.py              # FastAPI 应用入口
│  ├─ models.py            # SQLAlchemy 模型
│  ├─ schemas.py           # Pydantic 数据模型
│  ├─ requirements.txt
│  └─ run_backend.ps1      # Windows 后端启动脚本
│
├─ README.md
└─ .gitignore
```

## 本地运行

### 1. 准备环境

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Windows PowerShell

### 2. 创建数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE career_planner
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 3. 配置后端环境变量

在 `backend/.env` 中配置数据库和 AI 服务。该文件已被 `.gitignore` 忽略，不要提交真实密码或密钥。

```env
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=career_planner

MIMO_API_KEY=your_mimo_api_key
MIMO_API_URL=https://api.mimo-v2.com/v1
MIMO_MODEL=mimo-v2.5-pro
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=800
```

如果暂时没有 AI Key，登录、个人资料、职业推荐等基础功能仍可开发调试，但 AI 评估建议和规划生成会受影响。

### 4. 启动后端

推荐使用脚本：

```powershell
cd backend
.\run_backend.ps1
```

脚本会自动：

- 创建 `backend/venv`
- 安装 `requirements.txt`
- 检查数据库连接
- 启动 FastAPI 服务

默认后端地址：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

### 5. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

默认前端地址：

```text
http://localhost:5173
```

## 主要接口

### 用户

- `POST /auth/register`
- `POST /auth/login`

### 个人信息

- `GET /profile/{user_id}`
- `POST /profile/`
- `PUT /profile/{user_id}`
- `POST /profile/upload-avatar/{user_id}`

### 能力评估

- `GET /api/assessment/questions?type=tech`
- `GET /api/assessment/questions?type=general`
- `POST /api/assessment/submit`
- `GET /api/assessment/history/{user_id}`

### 职业推荐

- `GET /career/`
- `GET /career/seed-defaults`
- `GET /career/recommendation/{user_id}`
- `POST /career/recommendation/{user_id}`
- `GET /career/{career_id}`

### AI 规划

- `POST /api/planning/chat`
- `POST /api/planning/yearly-plan`

## 数据说明

- 后端启动时会自动创建缺失的数据表。
- 能力评估题目由后端默认题库初始化。
- 默认职业库由 `backend/routers/career.py` 初始化。
- 用户头像保存在 `backend/uploads/avatars/`。
- 年度规划结果保存在 `planning_yearly_plan_records` 表中，并按输入快照缓存。

## 注意事项

- `backend/.env` 不要提交到 GitHub。
- 当前项目适合课程设计、本地演示和继续开发，不建议直接作为生产系统部署。
- 如果后端接口返回 405 或旧字段，通常是后端没有重启到最新代码，重启 FastAPI 后再试。
- 如果 AI 请求失败，先检查 `MIMO_API_KEY`、`MIMO_API_URL`、`MIMO_MODEL` 和网络状态。
