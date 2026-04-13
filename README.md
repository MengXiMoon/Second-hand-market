# 二手交易市场项目 (Python + Vue)

这是一个基于 Python (FastAPI) 后端和 Vue 前端构建的二手交易市场系统。

## 功能特性

系统支持三种角色：
- **普通用户**：注册（需审核）、登录、查看商品、下单购买、管理个人订单、钱包管理（充值、查看记录）。
- **商家**：注册（需审核）、商品上架（需审核）、编辑商品、管理买家订单、钱包管理（提现、交易收益）。
- **管理员**：审核用户/商品、查看系统交易记录、手动充值、**自动收取交易佣金**。

### 核心业务逻辑
- **钱包系统**：用户可自行充值模拟资金。商家在销售商品后收入会自动打入钱包。
- **平台抽成**：每笔订单成交后，系统自动扣除 **1% 的平台手续费**，并存入管理员钱包。
- **提现功能**：商家可以将钱包内的余额进行“提现”操作，方便模拟资金流转。

## 环境要求
- **Python**: 推荐 3.8 或更高版本（已针对 3.12 版本修复了 `bcrypt` 兼容性问题）。
- **Node.js**: 推荐 18.x 或更高版本。

后端代码位于 `backend/` 目录下。

### 0. 进入后端目录
```powershell
cd backend
```

### 1. 创建并开启虚拟环境 (推荐)
为了保持环境隔离，建议先创建一个虚拟环境：

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 如果是 macOS/Linux 
# source venv/bin/activate
```

### 2. 安装依赖
```powershell
# 确保在 venv 激活状态下安装
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 3. 配置文件
在 `backend/` 目录下创建或编辑 `.env` 文件：
```env
PROJECT_NAME="Second Hand Market API"
DATABASE_URL="sqlite:///./sql_app.db"
SECRET_KEY="your_secret_key_here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 4. 运行程序
在 `backend/` 目录下运行：
```powershell
python -m app.main
```

### 5. API 交互文档
启动成功后，可以通过浏览器访问以下地址查看和测试接口：
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 前端开发 (Frontend)

项目根目录包含了基于 **Vue 3** 和 **Vite** 的前端开发环境。

### 1. 安装依赖
在项目根目录下运行：
```powershell
npm install
```

### 2. 启动开发服务器
```powershell
npm run dev
```
启动后，通常可以在 `http://localhost:5173` 访问前端界面。

### 3. 构建生产版本
如果您需要打包部署：
```powershell
npm run build
```
打包后的文件将生成在 `dist/` 目录下。

## 注意事项
- **注册审核**：新注册的用户默认是未审核状态，无法直接登录。您需要使用第一个注册的管理员账号，或直接修改数据库中的 `is_verified` 字段来通过审核。
- **商品审核**：商家上传的商品也需要管理员在后端进行 `approved` 操作后才会展示在首页。
