# 后端 AI 与部署说明

## 统一原则

本项目只保留一个 AI 调用入口：

```text
backend/llm_client.py
```

`PlanningAI` 和 `Assessment` 都从这里调用模型。队友的 `config.py`、`ai_service.py`、`ai_service_requests.py` 思路可以参考，但不要原样合并进项目，否则会出现两套 AI 配置、两个请求入口，后续很容易冲突。

## MiMo 配置

如果使用 Token Plan 的 `tp-` 开头 key，使用：

```env
MIMO_API_KEY=你的tp开头key
MIMO_API_URL=https://token-plan-cn.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=800
```

如果使用普通按量 API 的 `sk-` 开头 key，通常使用：

```env
MIMO_API_KEY=你的sk开头key
MIMO_API_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=800
```

如果没有写 `MIMO_API_URL`，`llm_client.py` 会根据 key 前缀自动选择默认地址：`tp-` 走 Token Plan 中国集群，其他 key 走普通 API 地址。

## 队友 pull 后启动后端

在 PowerShell 中运行：

```powershell
cd D:\Career\backend
.\run_backend.ps1
```

脚本会自动：

- 创建 `venv`
- 安装 `requirements.txt`
- 检查数据库连接
- 启动 FastAPI：`http://127.0.0.1:8000`

第一次运行前，需要先确认 `backend/.env` 已填写：

```env
DB_USERNAME=root
DB_PASSWORD=你的MySQL密码
DB_HOST=localhost
DB_PORT=3306
DB_NAME=career_planner
MIMO_API_KEY=你的MiMo key
MIMO_API_URL=https://token-plan-cn.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=800
```

## 数据库注意

当前项目使用 SQLAlchemy 的 `Base.metadata.create_all(bind=engine)` 自动创建缺失的表。它适合本地开发，但不会自动删除旧字段或复杂迁移。

如果队友数据库结构和你不一致，优先做法是：

1. 以你当前 `models.py` 为准。
2. 队友 pull 后运行 `run_backend.ps1`。
3. 如果报缺字段/表结构错误，再单独加迁移 SQL 或迁移脚本，不要让队友直接替换 `models.py`。
