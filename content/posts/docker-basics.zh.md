---
title: Docker 容器化实战：从入门到部署
summary: 全面介绍 Docker 容器技术，包括基本概念、常用命令、Dockerfile 编写和多容器编排，助你快速掌握容器化部署。
category: tech
created: 2024-02-20
updated: 2024-03-30
external_links:
  - platform: github
    url: https://github.com/yourname/docker-examples
---

# Docker 容器化实战：从入门到部署

Docker 改变了应用部署的方式。让我们一起探索容器化的魅力。

## 为什么选择 Docker？

### 核心优势
- **环境一致性**：开发、测试、生产环境完全一致
- **快速部署**：秒级启动，比虚拟机快得多
- **资源高效**：共享主机内核，占用资源少
- **易于管理**：简化依赖管理和版本控制

## Docker 基础概念

### 镜像 (Image)
只读模板，包含运行应用所需的一切。

### 容器 (Container)
镜像的运行实例，可以启动、停止、删除。

### 仓库 (Registry)
存储和分发镜像的服务，如 Docker Hub。

## 常用命令

```bash
# 拉取镜像
docker pull nginx:latest

# 运行容器
docker run -d -p 80:80 --name web nginx

# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 停止容器
docker stop web

# 删除容器
docker rm web

# 查看日志
docker logs web

# 进入容器
docker exec -it web bash
```

## 编写 Dockerfile

```dockerfile
# 使用官方 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

## 构建和运行

```bash
# 构建镜像
docker build -t myapp:v1 .

# 运行容器
docker run -d -p 8000:8000 --name myapp myapp:v1

# 查看运行状态
docker logs -f myapp
```

## Docker Compose

使用 `docker-compose.yml` 管理多容器应用：

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_PASSWORD=secret
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

运行 Compose：

```bash
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 最佳实践

### 1. 使用多阶段构建

```dockerfile
# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:18-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 2. 优化镜像大小

- 使用 Alpine 基础镜像
- 清理缓存和临时文件
- 合并 RUN 命令减少层数

### 3. 使用 .dockerignore

```
node_modules
.git
.env
*.md
.vscode
```

### 4. 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

## 生产环境部署

### 使用 Docker Swarm 或 Kubernetes
- **Docker Swarm**：简单易用，适合中小规模
- **Kubernetes**：功能强大，适合大规模集群

### 监控和日志
- 使用 Prometheus + Grafana 监控
- 集中式日志收集（ELK Stack）

## 常见问题

### Q: 容器数据持久化？
A: 使用 volumes 或 bind mounts

```bash
docker run -v /host/path:/container/path myapp
```

### Q: 如何限制资源？
A: 使用资源限制参数

```bash
docker run --memory="512m" --cpus="1.0" myapp
```

## 总结

Docker 让应用部署变得简单高效。关键要点：
- 理解镜像和容器的关系
- 编写优化的 Dockerfile
- 使用 Compose 管理多容器
- 遵循最佳实践

Happy containerizing! 🐳
