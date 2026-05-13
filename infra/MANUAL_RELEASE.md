# AstraFlow 手动发版与回滚流程

本文档用于服务器手动发版。当前阶段暂不做自动 CD，先用可控的手动流程：

```text
备份当前项目目录
备份数据库
拉取新代码
执行部署脚本
健康检查
异常时切回旧目录
```

## 1. 适用场景

适用于：

- 第二次及后续小版本发布。
- 还没有完整 CI/CD、蓝绿发布、镜像仓库版本管理的阶段。
- 发布内容主要是代码和前端静态资源变化。

不适合：

- 大规模数据库结构变更。
- 需要灰度发布的生产环境。
- 多台服务器同时发布。

## 2. 服务器目录约定

当前服务器目录按已有结构使用：

```text
/opt/astraflow/repo
```

版本备份目录：

```text
/opt/astraflow/releases
```

每次发布前，把当前 `repo` 复制到一个时间戳目录里：

```text
/opt/astraflow/releases/202605091517
```

这样不需要改线上项目目录名，线上始终使用 `/opt/astraflow/repo`。

## 3. 域名访问链路

域名不是和代码直接绑定的，完整链路是：

```text
用户浏览器
-> 域名 DNS A 记录解析到服务器公网 IP
-> 云服务器安全组 / 防火墙放行 80 或 443
-> 服务器端口进入 Docker Nginx
-> Nginx 托管前端静态资源，并把 /api 转发到 backend:8000
-> FastAPI 后端处理接口
```

当前 Compose 里 Nginx 的端口映射由 `infra/env/.env.prod` 控制：

```yaml
ports:
  - "${HTTP_PORT}:80"
  - "${HTTPS_PORT}:443"
```

如果 `HTTP_PORT=80`、`HTTPS_PORT=443`，域名可以直接打到 Docker Nginx。

如果 `HTTP_PORT=19000` 这类非标准端口，域名要正常使用 `http://域名` 或 `https://域名`，服务器前面通常还需要一个外层 Nginx，把 80 或 443 转发到本项目端口：

```nginx
server {
  listen 80;
  server_name your-domain.com;

  location / {
    proxy_pass http://127.0.0.1:19000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

项目内置的生产 Nginx 当前使用：

```nginx
server_name _;
```

这表示它不限制具体域名，凡是打到这个 Nginx 的请求都能接收。更严格的生产配置可以改成真实域名，例如：

```nginx
server_name your-domain.com www.your-domain.com;
```

排查域名是否正确打到项目，可以在服务器上看这几项：

```bash
docker compose --env-file infra/env/.env.prod -f infra/docker-compose.prod.yml ps
grep -E '^(HTTP_PORT|HTTPS_PORT|PUBLIC_ORIGIN|CORS_ORIGINS|NGINX_CONF)=' infra/env/.env.prod
curl -I "http://127.0.0.1:$(grep -E '^HTTP_PORT=' infra/env/.env.prod | cut -d '=' -f 2-)"
```

如果服务器还有外层 Nginx，再检查它是否转发到了本项目端口：

```bash
sudo nginx -T | grep -nE 'server_name|proxy_pass|19000|19443'
```

修改域名时通常要同步检查：

- DNS A 记录是否指向服务器公网 IP。
- 云服务器安全组是否放行 80 / 443。
- `PUBLIC_ORIGIN` 和 `CORS_ORIGINS` 是否改成真实域名。
- HTTPS 证书是否放到 `infra/certs`，并把 `NGINX_CONF` 切到 `nginx.prod.https.conf`。
- 开启 HTTPS 后，`GATE_COOKIE_SECURE` 应改为 `true`。

## 4. 发布前检查

进入项目目录：

```bash
cd /opt/astraflow/repo
```

确认当前分支和提交：

```bash
git branch --show-current
git log --oneline -5
```

确认生产环境变量存在：

```bash
test -f infra/env/.env.prod && echo "env ok"
```

确认当前服务状态：

```bash
docker compose --env-file infra/env/.env.prod -f infra/docker-compose.prod.yml ps
```

确认当前健康检查正常：

```bash
curl -fsS "$(grep -E '^HEALTHCHECK_URL=' infra/env/.env.prod | cut -d '=' -f 2-)"
```

如果发布前健康检查已经失败，先不要发版，先排查当前线上问题。

## 5. 备份当前项目目录

在 `/opt/astraflow` 下备份当前 `repo` 目录：

```bash
cd /opt/astraflow
mkdir -p releases
release_id="$(date +%Y%m%d%H%M)"
cp -a repo "releases/$release_id"
echo "Backup release: /opt/astraflow/releases/$release_id"
```

查看刚生成的备份：

```bash
ls -lt releases | head
```

这个目录就是回滚时要切回的“老包”。

## 6. 备份数据库

```bash
cd /opt/astraflow/repo
./infra/scripts/backup-db.sh
```

默认备份位置：

```text
/opt/astraflow/backups/postgres
```

确认备份文件存在：

```bash
ls -lt /opt/astraflow/backups/postgres | head
```

## 7. 拉取新代码

```bash
cd /opt/astraflow/repo
git pull origin master
```

确认新提交：

```bash
git log --oneline -5
```

## 8. 执行部署

```bash
cd /opt/astraflow/repo
./infra/scripts/deploy-prod.sh
```

这个脚本会执行：

```text
docker compose config 校验
docker compose up -d --build --remove-orphans
alembic upgrade head
python -m app.db.init_db
健康检查
```

## 9. 发布后验证

健康检查：

```bash
curl -fsS "$(grep -E '^HEALTHCHECK_URL=' infra/env/.env.prod | cut -d '=' -f 2-)"
```

容器状态：

```bash
docker compose --env-file infra/env/.env.prod -f infra/docker-compose.prod.yml ps
```

查看关键日志：

```bash
docker compose --env-file infra/env/.env.prod -f infra/docker-compose.prod.yml logs --tail=120 backend nginx
```

浏览器验证：

```text
1. 打开线上入口。
2. 通过访问门禁。
3. 登录 admin 或测试账号。
4. 进入系统页。
5. 点击“后端联调检查”的两个按钮。
6. 进入管理系统，确认子应用能加载。
```

## 10. 回滚代码目录

如果发布后出现问题，先找最近一次备份目录：

```bash
cd /opt/astraflow
ls -lt releases | head
```

假设要回滚到：

```text
/opt/astraflow/releases/202605091517
```

执行：

```bash
cd /opt/astraflow
mv repo "repo-bad-$(date +%Y%m%d%H%M)"
cp -a releases/202605091517 repo
cd repo
docker compose --env-file infra/env/.env.prod -f infra/docker-compose.prod.yml up -d --build --remove-orphans
```

回滚后验证：

```bash
curl -fsS "$(grep -E '^HEALTHCHECK_URL=' infra/env/.env.prod | cut -d '=' -f 2-)"
docker compose --env-file infra/env/.env.prod -f infra/docker-compose.prod.yml ps
```

## 11. 是否需要恢复数据库

一般小版本发布不需要恢复数据库。

本次是否需要恢复数据库，按这个判断：

```text
没有新增 Alembic migration：通常不需要恢复数据库。
只改前端、后端普通接口：通常不需要恢复数据库。
新增字段但兼容旧代码：一般可以只回滚代码。
删除字段、改字段类型、清洗数据失败：可能需要恢复数据库。
```

恢复数据库属于高风险操作，执行前必须确认：

- 要恢复到哪个备份文件。
- 恢复会覆盖哪些线上数据。
- 发布后是否已有新数据写入。

当前阶段如果只是普通代码发布，优先使用“代码目录回滚”，不要轻易恢复数据库。

## 12. 当前阶段不做自动 CD 的原因

暂时不建议 push 后自动发布到服务器。

原因：

- 备份和回滚流程还需要先手动跑熟。
- 生产环境变量、服务器密钥、数据库备份都还需要更严格管理。
- 当前是学习阶段，手动发布更容易理解每一步出了问题该怎么定位。

推荐下一步先做 CI：

```text
后端 pytest
前端 pnpm build
docker compose config
```

等手动发布稳定 2-3 次，再考虑自动 CD。
