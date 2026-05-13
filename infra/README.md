# AstraFlow Infra

本目录放第一阶段基础设施：

- `docker-compose.local.yml`：本地 Docker Compose。默认只启动 PostgreSQL、Redis；使用 `--profile full` 时启动 `backend-api`、`ai-gateway`、`llm-provider`、多个 Vite 前端子应用和 Nginx。
- `nginx/nginx.local.conf`：本地反向代理，`/api` 转发到后端。
- `scripts/dev-up.sh`：一键启动全量 Docker 环境。
- `scripts/dev-down.sh`：停止全量 Docker 环境。
- `scripts/debug-infra-up.sh`：本地断点调试时只启动 PostgreSQL 和 Redis。
- `scripts/init-db.sh`：本地开发时初始化数据库。
- `docker-compose.prod.yml`：生产部署 Compose，前端静态资源由 Nginx 托管。
- `env/.env.prod.example`：生产环境变量模板，复制成 `.env.prod` 后填写真实值。
- `env/.env.local.example`：本地大模型环境变量模板，复制成 `.env.local` 后填写真实值。
- `nginx/nginx.prod.conf`：HTTP 版本生产 Nginx，适合首次无证书验证。
- `nginx/nginx.prod.https.conf`：HTTPS 版本生产 Nginx，证书就绪后切换使用。
- `scripts/deploy-prod.sh`：生产手动部署脚本，包含构建、启动、迁移、初始化和健康检查。
- `scripts/backup-db.sh`：生产 PostgreSQL 备份脚本。
- `MANUAL_RELEASE.md`：服务器手动发版与回滚流程。

## 本地全量 Docker

适合验证完整 Docker/Nginx 环境：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
cp infra/env/.env.local.example infra/env/.env.local
vim infra/env/.env.local
./infra/scripts/dev-up.sh
```

本地 Nginx 入口：

```bash
http://localhost:18000
```

阶段 2 本地服务端口：

```text
backend-api:       http://localhost:18080/api/health
ai-gateway:        http://localhost:18081/health
llm-provider:      http://localhost:18082/health
```

如果暂时不接真实大模型，可以不创建 `infra/env/.env.local`，本地会继续使用默认 mock 链路。

真实配置只放在 env 文件里：

```text
本地：infra/env/.env.local
生产：infra/env/.env.prod
```

`backend/app/core/config.py` 只声明代码会读取哪些配置；`docker-compose.*.yml` 只负责把 env 文件里的变量传给容器，不要在这些文件里填写真实 API Key。

## 本地断点调试基础设施

适合前端、后端在本机启动，只保留 PostgreSQL 和 Redis 在 Docker 中运行：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
./infra/scripts/debug-infra-up.sh
```

端口：

```text
PostgreSQL: localhost:15432
Redis:      localhost:16379
```

后端本地进程连接 `localhost:15432` 和 `localhost:16379`。Docker 后端连接 `postgres:5432` 和 `redis:6379`，两套配置不要混用。

生产部署入口：

```bash
cp infra/env/.env.prod.example infra/env/.env.prod
vim infra/env/.env.prod
./infra/scripts/deploy-prod.sh
```

第二次及后续发版先看：

```text
infra/MANUAL_RELEASE.md
```
