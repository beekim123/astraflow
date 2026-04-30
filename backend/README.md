# AstraFlow Backend

第一阶段后端是一个模块化单体，负责平台底座：

- FastAPI + Pydantic v2
- SQLAlchemy 2.x AsyncSession + asyncpg
- PostgreSQL 持久化
- Redis 访问门禁验证码
- JWT + Refresh Token
- RBAC 权限、动态菜单
- 操作日志和 RequestID
- AI 边界预留：`AgentClient` + `MockAgentClient`

## 本地开发

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --reload --port 18080
```

Swagger：

```text
http://localhost:18080/docs
```

默认账号：

```text
admin / Admin@123456
member / Member@123456
```

## 测试

基础测试不依赖真实数据库：

```bash
pytest
```

登录成功测试需要先启动 PostgreSQL 并初始化种子数据：

```bash
RUN_DB_TESTS=1 pytest app/tests/test_auth.py
```

## 第一阶段故意不做

- 不接真实大模型。
- 不做 RAG。
- 不做 OCR。
- 不拆微服务。
- 不接 Nacos。

第二阶段会把 `MockAgentClient` 替换为调用 `ai-gateway` 的 HTTP 客户端，再由 `ai-gateway` 统一转发到 MCP 服务。
