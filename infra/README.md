# AstraFlow Infra

本目录放第一阶段基础设施：

- `docker-compose.local.yml`：PostgreSQL、Redis、Backend、多个 Vite 前端子应用、Nginx。
- `nginx/nginx.local.conf`：本地反向代理，`/api` 转发到后端。
- `scripts/dev-up.sh`：一键启动。
- `scripts/dev-down.sh`：停止服务。
- `scripts/init-db.sh`：本地开发时初始化数据库。
- `docker-compose.prod.yml`：生产部署 Compose，前端静态资源由 Nginx 托管。
- `env/.env.prod.example`：生产环境变量模板，复制成 `.env.prod` 后填写真实值。
- `nginx/nginx.prod.conf`：HTTP 版本生产 Nginx，适合首次无证书验证。
- `nginx/nginx.prod.https.conf`：HTTPS 版本生产 Nginx，证书就绪后切换使用。
- `scripts/deploy-prod.sh`：生产手动部署脚本，包含构建、启动、迁移、初始化和健康检查。
- `scripts/backup-db.sh`：生产 PostgreSQL 备份脚本。

本地 Nginx 入口：

```bash
http://localhost:18000
```

生产部署入口：

```bash
cp infra/env/.env.prod.example infra/env/.env.prod
vim infra/env/.env.prod
./infra/scripts/deploy-prod.sh
```
