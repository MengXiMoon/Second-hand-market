"""
生成中量二手商品测试数据和商家用户

使用方法:
    cd backend
    python init_test_data.py

数据量:
    - 5 个商家用户
    - 3 个普通买家用户
    - 30 个二手商品（覆盖待审核/已上架/已拒绝/已售罄状态，覆盖多品类）
"""
import secrets
from app.db.session import SessionLocal, engine, Base
from app.models.models import User, UserRole, Product, ProductStatus, Wallet
from app.core import security

# 确保表已创建
Base.metadata.create_all(bind=engine)

PASSWORD = "123456"

# ---- 商家用户 ----
MERCHANTS = [
    ("phone_merchant", "phone@test.com", "手机数码专营店"),
    ("book_merchant", "book@test.com", "旧书流动书店"),
    ("furniture_merchant", "furniture@test.com", "宜家二手家具"),
    ("cloth_merchant", "cloth@test.com", "闲置衣橱"),
    ("elec_merchant", "elec@test.com", "小家电杂货铺"),
]

# ---- 普通买家 ----
BUYERS = [
    ("buyer1", "buyer1@test.com"),
    ("buyer2", "buyer2@test.com"),
    ("buyer3", "buyer3@test.com"),
]

# ---- 商品模板 (name, description, price_yuan, stock) ----
PHONE_PRODUCTS = [
    ("iPhone 13 128G 午夜色", "95新，无划痕，电池健康89%，带原装充电器", 320000, 1),
    ("iPhone 14 Pro 256G 暗紫色", "99新，激活仅一个月，配件齐全，保修到年底", 620000, 1),
    ("华为 Mate 60 Pro 512G", "全新未拆封，雅丹黑，昆仑玻璃版", 699900, 2),
    ("小米14 Ultra 16+512G", "9成新，拍照神器，徕卡光学镜头，送保护壳", 420000, 1),
    ("三星 S24+ 256G", "国行在保，使用3个月，钴蓝配色，箱说全", 480000, 1),
    ("一加 Ace 3 Pro 512G", "95新，性能怪兽，游戏流畅，超级闪充", 280000, 1),
]

BOOK_PRODUCTS = [
    ("《三体》全三册 精装版", "刘慈欣著，9成新，无折痕无笔记，科幻迷必入", 5800, 1),
    ("《深入理解计算机系统》原书第3版", "CSAPP经典教材，8成新，部分章节有标注", 4500, 2),
    ("《百年孤独》精装插图版", "马尔克斯经典，全新仅拆封，收藏级品相", 3900, 1),
    ("《Python编程：从入门到实践》第3版", "95新，适合零基础入门，代码示例完整", 3500, 3),
    ("《设计模式：可复用面向对象软件的基础》", "GoF经典，英文原版，9成新", 6800, 1),
    ("《明朝那些事儿》全套9册", "当年明月著，8成新，历史入门佳作", 8800, 1),
]

FURNITURE_PRODUCTS = [
    ("宜家 MALM 马尔姆办公桌 140x65cm", "白色，使用一年，轻微使用痕迹，配件齐全", 35000, 1),
    ("电竞椅 傲风C3 黑色", "使用半年，带头枕腰靠，坐着舒服，搬家急出", 58000, 1),
    ("北欧风实木书架 6层", "橡木色，尺寸180x80x30cm，承重好，9成新", 68000, 1),
    ("折叠餐桌 宜家 NORDEN 诺顿", "桦木色，可展开至152cm，适合小户型", 42000, 1),
    ("乳胶床垫 1.8m x 2m 20cm厚", "天然乳胶，软硬适中，仅用3个月，无污渍", 78000, 1),
    ("落地灯 简约北欧风", "三档调光，暖白光，金属灯杆+布艺灯罩", 8500, 2),
]

CLOTH_PRODUCTS = [
    ("北面 1996 经典羽绒服 男款L码", "黑色，正品，穿一季，保暖效果一流", 58000, 1),
    ("Nike Air Jordan 1 Low 倒钩", "42码，仅试穿，原盒原标，收藏自用皆可", 128000, 1),
    ("优衣库 轻薄羽绒背心 女款M码", "米白色，穿两次，轻便保暖易收纳", 8900, 2),
    ("Levi's 501 经典直筒牛仔裤 W32L32", "美产，养牛半年，已脱浆，落色自然", 15800, 1),
    ("Arc'teryx Beta AR 冲锋衣 男款XL", "黑色GTX面料，防水透气，户外必备", 168000, 1),
]

ELEC_PRODUCTS = [
    ("戴森 V12 Detect Slim 无线吸尘器", "激光探测灰尘，使用半年，续航正常，配件全", 168000, 1),
    ("飞利浦空气炸锅 HD9650", "XXL大容量，9成新，做过几次炸鸡，功能正常", 38000, 1),
    ("小米即热饮水机 S1", "3秒速热，多档温度，桌面款，轻微使用痕迹", 12800, 1),
    ("石头扫地机器人 P10 Pro", "扫拖一体，自动集尘，用3个月，打扫干净省心", 158000, 1),
    ("德龙全自动咖啡机 Magnifica S", "意式浓缩、美式一键出品，使用一年，定期除垢保养", 120000, 1),
    ("华为路由器 AX6", "Wi-Fi 6+，7200Mbps，穿墙能力强，覆盖150平", 18500, 2),
]


def create_users(db):
    """创建商家和买家用户，返回 {username: user_obj}"""
    user_map = {}

    for username, email, _ in MERCHANTS:
        exists = db.query(User).filter(User.username == username).first()
        if not exists:
            u = User(
                username=username,
                email=email,
                hashed_password=security.get_password_hash(PASSWORD),
                role=UserRole.MERCHANT,
                is_verified=True,
            )
            db.add(u)
            db.flush()
            db.add(Wallet(user_id=u.id, balance=0))
            user_map[username] = u
        else:
            user_map[username] = exists

    for username, email in BUYERS:
        exists = db.query(User).filter(User.username == username).first()
        if not exists:
            u = User(
                username=username,
                email=email,
                hashed_password=security.get_password_hash(PASSWORD),
                role=UserRole.USER,
                is_verified=True,
            )
            db.add(u)
            db.flush()
            db.add(Wallet(user_id=u.id, balance=0))
            user_map[username] = u
        else:
            user_map[username] = exists

    db.commit()
    return user_map


def create_products(db, user_map):
    """批量创建商品，覆盖不同状态"""
    # 商品定义: (name, description, price_cents, stock, status, merchant_key)
    product_defs = []

    # 手机数码 → phone_merchant
    for i, (name, desc, price, stock) in enumerate(PHONE_PRODUCTS):
        status = ProductStatus.APPROVED
        if i == 0:
            status = ProductStatus.PENDING
        elif i == 1:
            status = ProductStatus.REJECTED
        elif i == len(PHONE_PRODUCTS) - 1:
            status = ProductStatus.SOLD_OUT
        product_defs.append((name, desc, price, stock, status, "phone_merchant"))

    # 图书 → book_merchant
    for i, (name, desc, price, stock) in enumerate(BOOK_PRODUCTS):
        status = ProductStatus.APPROVED
        if i == 0:
            status = ProductStatus.PENDING
        elif i == len(BOOK_PRODUCTS) - 1:
            status = ProductStatus.SOLD_OUT
        product_defs.append((name, desc, price, stock, status, "book_merchant"))

    # 家具 → furniture_merchant
    for i, (name, desc, price, stock) in enumerate(FURNITURE_PRODUCTS):
        status = ProductStatus.APPROVED
        if i == 0:
            status = ProductStatus.PENDING
        elif i == len(FURNITURE_PRODUCTS) - 1:
            status = ProductStatus.REJECTED
        product_defs.append((name, desc, price, stock, status, "furniture_merchant"))

    # 衣物 → cloth_merchant
    for i, (name, desc, price, stock) in enumerate(CLOTH_PRODUCTS):
        status = ProductStatus.APPROVED
        if i == 0:
            status = ProductStatus.PENDING
        product_defs.append((name, desc, price, stock, status, "cloth_merchant"))

    # 小家电 → elec_merchant
    for i, (name, desc, price, stock) in enumerate(ELEC_PRODUCTS):
        status = ProductStatus.APPROVED
        if i == 0:
            status = ProductStatus.PENDING
        elif i == len(ELEC_PRODUCTS) - 1:
            status = ProductStatus.SOLD_OUT
        product_defs.append((name, desc, price, stock, status, "elec_merchant"))

    count = 0
    for name, desc, price, stock, status, merchant_key in product_defs:
        exists = db.query(Product).filter(Product.name == name).first()
        if exists:
            continue
        p = Product(
            name=name,
            description=desc,
            price=price,
            stock=stock,
            status=status,
            merchant_id=user_map[merchant_key].id,
            audit_remark=("描述与实际不符，请重新修改" if status == ProductStatus.REJECTED else None),
        )
        db.add(p)
        count += 1

    db.commit()
    return count


def main():
    db = SessionLocal()
    try:
        print("=" * 55)
        print("  二手市场 — 测试数据生成器")
        print("=" * 55)

        user_map = create_users(db)
        print(f"\n[用户] 创建/确认 {len(user_map)} 个用户:")
        for uname, u in user_map.items():
            role_cn = {"merchant": "商家", "user": "买家", "admin": "管理员"}.get(u.role.value, u.role.value)
            print(f"  {uname:20s}  {role_cn:4s}  密码: {PASSWORD}")

        product_count = create_products(db, user_map)
        print(f"\n[商品] 创建 {product_count} 个二手商品")
        print("  状态分布:")
        for s in ProductStatus:
            c = db.query(Product).filter(Product.status == s).count()
            if c > 0:
                label = {"pending": "待审核", "approved": "已上架", "rejected": "已拒绝", "sold_out": "已售罄"}[s.value]
                print(f"    {label}: {c} 件")

        print(f"\n[管理员] 账号: admin  密码: (首次启动时打印)")
        print(f"[管理员端]  访问: http://localhost:5173/admin/login")
        print(f"[商家端]    访问: http://localhost:5173/merchant/login")
        print(f"\n所有测试账号密码均为: {PASSWORD}")
        print("=" * 55)

    except Exception as e:
        print(f"错误: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
