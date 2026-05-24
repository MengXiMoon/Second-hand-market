#!/bin/bash
# =============================================
#  Second-hand Market - Ubuntu 云服务器一键部署
#  用法: chmod +x deploy.sh && sudo ./deploy.sh
# =============================================
set -e

# ---- 请修改这里为你的服务器 IP 或域名 ----
SERVER_IP="192.168.56.102"
# SERVER_IP="123.45.67.89"
# SERVER_IP="example.com"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR"

echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN}  Second-hand Market - Ubuntu 云服务器部署脚本${NC}"
echo -e "${CYAN}===============================================${NC}"

# ---- 获取服务器 IP ----
if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -1)
    if [ -z "$SERVER_IP" ]; then
        SERVER_IP=$(hostname -I | awk '{print $1}')
    fi
fi

echo -e "\n${GREEN}[信息] 服务器 IP/域名: $SERVER_IP${NC}"
if [ -z "$SERVER_IP" ]; then
    echo -e "${RED}[错误] 无法自动检测服务器 IP，请在 deploy.sh 开头手动设置 SERVER_IP${NC}"
    exit 1
fi

# ---- 权限准备 ----
ACTUAL_USER="${SUDO_USER:-$USER}"
HOME_DIR=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)
echo -e "${GREEN}[信息] 运行用户: $ACTUAL_USER, 家目录: $HOME_DIR${NC}"

# 确保 nginx 能访问用户家目录（否则 dist/ 报 403）
if [ -d "$HOME_DIR" ]; then
    chmod o+x "$HOME_DIR" 2>/dev/null || true
fi

# 修复之前 sudo 构建导致的 root 所有权问题
for dir in dist node_modules; do
    if [ -d "$FRONTEND_DIR/$dir" ]; then
        chown -R "$ACTUAL_USER:$ACTUAL_USER" "$FRONTEND_DIR/$dir" 2>/dev/null || true
    fi
done
chown "$ACTUAL_USER:$ACTUAL_USER" "$FRONTEND_DIR/.env.production" 2>/dev/null || true
chown "$ACTUAL_USER:$ACTUAL_USER" "$BACKEND_DIR/.env" 2>/dev/null || true

# =============================================
# 1. 安装系统依赖
# =============================================
echo -e "\n${CYAN}[1/7] 安装系统依赖...${NC}"
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential libffi-dev libssl-dev nginx curl

# 安装 Node.js 22.x (via NodeSource)
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# 如果已安装但版本太旧，强制升级到 22
NODE_MAJOR=$(node -v 2>/dev/null | cut -d. -f1 | tr -d 'v')
if [ "$NODE_MAJOR" -lt 20 ]; then
    echo -e "${YELLOW}  Node.js 版本过低 (v$NODE_MAJOR)，升级到 22.x...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi
echo -e "${GREEN}  Python: $(python3 --version)${NC}"
echo -e "${GREEN}  Node:   $(node --version)${NC}"
echo -e "${GREEN}  npm:    $(npm --version)${NC}"

# =============================================
# 2. 后端环境搭建
# =============================================
echo -e "\n${CYAN}[2/7] 配置后端 Python 虚拟环境...${NC}"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

# 生成 .env（如果不存在）
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}  生成后端 .env 配置...${NC}"
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    cat > .env << ENVEOF
PROJECT_NAME="Second Hand Market API"
DATABASE_URL="sqlite:///./sql_app.db"
SECRET_KEY="$SECRET_KEY"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["*"]
UPLOAD_DIR="static/uploads"
ENVEOF
    # 修正文件所有权（sudo 下生成的文件属 root）
    if [ -n "$SUDO_USER" ]; then
        chown "$SUDO_USER:$SUDO_USER" .env
    fi
fi

deactivate

# =============================================
# 3. 初始化数据库和管理员
# =============================================
echo -e "\n${CYAN}[3/7] 初始化数据库...${NC}"
cd "$BACKEND_DIR"
source venv/bin/activate
if [ ! -f "sql_app.db" ]; then
    python3 init_test_data.py
else
    echo -e "${YELLOW}  数据库已存在，跳过初始化${NC}"
fi
deactivate

# =============================================
# 4. 前端构建
# =============================================
echo -e "\n${CYAN}[4/7] 构建前端...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    npm install
elif [ ! -f "node_modules/.package-lock.json" ]; then
    echo -e "${YELLOW}  node_modules 不完整，重新安装...${NC}"
    rm -rf node_modules
    npm install
fi

# 确保前端文件所有者为正确用户
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$FRONTEND_DIR/dist" 2>/dev/null || true
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$FRONTEND_DIR/node_modules" 2>/dev/null || true

# 写入生产环境配置
cat > .env.production << ENVEOF
VITE_API_BASE_URL=/v1
VITE_WS_BASE_URL=ws://$SERVER_IP/v1
VITE_STATIC_BASE_URL=
ENVEOF

npm run build
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$FRONTEND_DIR/dist" 2>/dev/null || true
chmod -R o+rX "$FRONTEND_DIR/dist" 2>/dev/null || true
echo -e "${GREEN}  前端构建完毕 → dist/${NC}"

# =============================================
# 5. 配置 nginx
# =============================================
echo -e "\n${CYAN}[5/7] 配置 nginx...${NC}"

sudo tee /etc/nginx/sites-available/second-hand-market > /dev/null << NGINXEOF
server {
    listen 80;
    server_name $SERVER_IP;

    # gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;
    gzip_min_length 256;

    # 前端静态文件
    root $FRONTEND_DIR/dist;
    index index.html;

    # 静态资源缓存
    location /assets/ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # API 反向代理
    location /v1/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 10m;
    }

    # WebSocket 代理
    location /v1/ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }

    # 静态文件（上传图片等）
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # SPA fallback：所有其他路径返回 index.html
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/second-hand-market /etc/nginx/sites-enabled/
# 仅移除默认站点（如果存在且为标准配置）
if [ -f /etc/nginx/sites-enabled/default ]; then
    if grep -q "Welcome to nginx" /etc/nginx/sites-enabled/default 2>/dev/null; then
        sudo rm -f /etc/nginx/sites-enabled/default
    fi
fi
sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}  nginx 配置完成${NC}"

# =============================================
# 6. 配置 systemd 服务（开机自启）
# =============================================
echo -e "\n${CYAN}[6/7] 配置 systemd 后台服务...${NC}"

# 用非 root 用户运行
SERVICE_USER="$ACTUAL_USER"

sudo tee /etc/systemd/system/second-hand-market.service > /dev/null << SYSTEMDEOF
[Unit]
Description=Second-hand Market Backend
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SYSTEMDEOF

sudo systemctl daemon-reload
sudo systemctl enable second-hand-market
sudo systemctl restart second-hand-market
echo -e "${GREEN}  systemd 服务已启动${NC}"

# =============================================
# 7. 完成
# =============================================
echo -e "\n${CYAN}===============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${CYAN}===============================================${NC}"
echo -e ""
echo -e "  前端页面:  ${GREEN}http://$SERVER_IP${NC}"
echo -e "  API 文档:  ${GREEN}http://$SERVER_IP/v1/docs${NC}"
echo -e "  管理端:    ${GREEN}http://$SERVER_IP/admin/login${NC}"
echo -e "  商家端:    ${GREEN}http://$SERVER_IP/merchant/login${NC}"
echo -e ""
echo -e "  管理员密码: ${YELLOW}查看后端终端输出或 sql_app.db${NC}"
echo -e "  测试账号密码: ${YELLOW}123456${NC}"
echo -e ""
echo -e "  服务管理:"
echo -e "    查看状态:  ${CYAN}sudo systemctl status second-hand-market${NC}"
echo -e "    重启服务:  ${CYAN}sudo systemctl restart second-hand-market${NC}"
echo -e "    查看日志:  ${CYAN}sudo journalctl -u second-hand-market -f${NC}"
echo -e "    nginx 重启: ${CYAN}sudo systemctl reload nginx${NC}"
echo -e ""
echo -e "  ${YELLOW}提示: 如果无法访问，请检查云服务器安全组是否放行 80 端口${NC}"
