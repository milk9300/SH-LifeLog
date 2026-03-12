# Build stage
FROM node:22-slim as build-stage
WORKDIR /app
COPY package*.json ./
# 强制清除以前由于不同 registry 导致的 lock 冲突，如果网络不好则尝试官方源或镜像源
RUN npm install --registry=https://registry.npmmirror.com --no-audit --no-fund --legacy-peer-deps
COPY . .
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# 复制自定义 Nginx 配置以支持 SPA 路由刷新
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
