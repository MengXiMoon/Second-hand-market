# 二手交易市场 (Second-hand Market)

基于 Python FastAPI + Vue 3 的在线二手商品交易平台，支持三端登录隔离、实时通信、钱包交易、平台抽成。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python) |
| 前端框架 | Vue 3 + Vite + Element Plus |
| 数据库 | SQLite (SQLAlchemy ORM) |
| 认证 | JWT (OAuth2 Password Bearer) + bcrypt |
| 实时通信 | WebSocket |
| 部署 | nginx + systemd (Ubuntu) |

## 功能概览

### 买家用户
- 注册登录（管理员审核）、浏览商品、搜索筛选
- 加入购物车、下单购买、钱包充值/提现
- 订单管理、实时私信聊天（与卖家跨机器通信）
- 商品收藏（心愿单）

### 商家
- 商品上架/编辑/下架（管理员审核）
- 销售记录查看、收入自动入账
- 与买家实时聊天

### 管理员
- 用户审核（通过/拒绝）、商品审核（通过/拒绝，含驳回理由）
- 全站订单/用户/商品管理、批量操作
- 手动充值/退款、交易流水查看
- 管理员仪表板、数据导出

### 核心业务
- **钱包系统**：用户充值 → 购买扣款 → 平台扣 1% 佣金 → 商家收款
- **商品审核流程**：商家提交 → 管理员审批/驳回 → 驳回后可修改重新提交
- **订单状态机**：ordered → paid → shipped → completed / cancelled / refund
- **登录互斥**：同一账号只能在一台设备在线，先登录者不被顶号
- **实时通知**：WebSocket 推送注册审核、商品审核、新订单、新消息

## 快速开始

### Windows 本地开发

```powershell
# 一键启动
.\OneClickStart.ps1
```

或者分别启动：

```powershell
# 终端 1 — 后端
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m app.main                    # → http://localhost:8000

# 终端 2 — 前端
npm install
npm run dev                           # → http://localhost:5173
```

### Ubuntu 云服务器部署

```bash
cd Second-hand-market
chmod +x deploy.sh
sudo ./deploy.sh
```

部署后访问 `http://<服务器IP>`，自动化完成 nginx 反向代理 + systemd 自启 + 数据库初始化 + 前端构建。

## 管理员 & 测试账号

首次启动后端时，管理员密码随机生成并打印在终端。

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | 启动时随机生成（或设置 `ADMIN_INIT_PASSWORD`） |
| 商家 | phone_merchant / book_merchant / cloth_merchant / furniture_merchant / elec_merchant | 123456 |
| 买家 | buyer1 / buyer2 / buyer3 | 123456 |

生成 30 件测试商品：

```bash
cd backend
python init_test_data.py
```

## 项目结构

```
Second-hand-market/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                # 认证依赖注入
│   │   │   └── v1/
│   │   │       ├── api.py             # 路由注册
│   │   │       └── endpoints/         # auth / users / products / orders / wallet / chat / websockets
│   │   ├── core/
│   │   │   ├── config.py              # 配置管理 (pydantic-settings)
│   │   │   ├── security.py            # JWT + bcrypt
│   │   │   ├── session_manager.py     # 登录互斥会话管理
│   │   │   └── websocket_manager.py   # WebSocket 连接管理
│   │   ├── db/
│   │   │   └── session.py             # SQLAlchemy 数据库连接
│   │   ├── models/
│   │   │   └── models.py              # 数据模型 (User / Product / Order / Wallet / Chat)
│   │   ├── schemas/                   # Pydantic 请求/响应模型
│   │   ├── services/                  # 业务逻辑 (order_service / chat_service)
│   │   └── main.py                    # FastAPI 入口
│   ├── init_admin.py                  # 管理员初始化
│   ├── init_test_data.py              # 测试数据生成
│   ├── requirements.txt
│   └── run_server.ps1                 # Windows 后端启动脚本
├── src/
│   ├── api/                           # 前端 HTTP 请求封装
│   ├── components/                    # 公共组件 (Layout / Navbar)
│   ├── router/                        # 路由配置（三端路由）
│   ├── store/                         # 状态管理（三端会话隔离）
│   ├── utils/                         # 工具函数 (格式化 / 状态映射)
│   └── views/                         # 页面视图
│       ├── Login.vue / Register.vue / Home.vue / Products.vue
│       ├── Orders.vue / Wallet.vue / Chat.vue / MyProducts.vue / Sales.vue
│       └── admin/                     # 管理端页面
├── deploy.sh                          # Ubuntu 一键部署脚本
├── OneClickStart.ps1                  # Windows 一键启动脚本
├── vite.config.js
└── package.json
```

## 部署架构

```
浏览器 (任意机器)
    │
    ▼
┌──────────────────────────┐
│  nginx :80               │
│  ├─ /           → 前端   │  dist/ 静态文件
│  ├─ /v1/        → 后端   │  proxy_pass → uvicorn :8000
│  ├─ /v1/ws/     → WS    │  WebSocket 代理 (Upgrade)
│  └─ /static/    → 文件   │  上传图片
└──────────────────────────┘
         │
    uvicorn :8000 (systemd 管理，开机自启)
         │
    SQLite (sql_app.db)
```

## API 文档

启动后端后访问：
- Swagger UI: `http://<host>:8000/docs`
- ReDoc: `http://<host>:8000/redoc`

## 环境变量

### 后端 (.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./sql_app.db` |
| `SECRET_KEY` | JWT 签名密钥 | 自动生成 |
| `CORS_ORIGINS` | 跨域白名单 | `["*"]` |
| `UPLOAD_DIR` | 上传文件目录 | `static/uploads` |
| `ALLOW_SELF_RECHARGE` | 允许自充值 | `true` |

### 前端 (.env.production)

| 变量 | 说明 |
|------|------|
| `VITE_API_BASE_URL` | API 地址（nginx 代理下填 `/v1`） |
| `VITE_WS_BASE_URL` | WebSocket 地址 |
| `VITE_STATIC_BASE_URL` | 静态文件地址 |

## 许可证

MIT
