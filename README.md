# 大学生智能职业规划系统 - 基础环境说明

## 1. 当前项目状态
目前已完成第一阶段基础环境搭建，包括：

- 前端 Vue3 + Vite 项目初始化
- Vue Router 路由配置
- Pinia 状态管理基础配置
- Landing 主页面壳子
- Register 页面壳子
- FastAPI 后端初始化
- /test 测试接口
- MySQL 数据库安装与配置
- career_planner 数据库创建
- database.py 数据库连接
- /db-test 数据库测试接口

---

## 2. 项目目录结构

```text
Career/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── router/
│   │   ├── stores/
│   │   └── views/
│   ├── package.json
│   └── ...
├── backend/
│   ├── venv/
│   ├── main.py
│   ├── database.py
│   ├── test_db.py
│   ├── requirements.txt
│   └── ...