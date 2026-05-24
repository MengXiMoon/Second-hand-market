"""
生成大量二手商品测试数据

使用方法:
    cd backend
    python init_test_data.py

数据量:
    - 8 个商家用户 + 10 个买家 + 1 管理员
    - 70+ 件二手商品（覆盖全部 7 个分类、4 种状态）
    - 买家钱包预充值，方便测试购买流程
"""
from app.db.session import SessionLocal, engine, Base
from app.models.models import User, UserRole, Product, ProductStatus, Wallet, Transaction, TransactionType
from app.core import security

Base.metadata.create_all(bind=engine)

PASSWORD = "123456"

MERCHANTS = [
    ("phone_m", "phone@test.com"),
    ("book_m", "book@test.com"),
    ("furniture_m", "furniture@test.com"),
    ("cloth_m", "cloth@test.com"),
    ("elec_m", "elec@test.com"),
    ("sports_m", "sports@test.com"),
    ("digital_m", "digital@test.com"),
    ("toy_m", "toy@test.com"),
]

BUYERS = [
    ("张三", "zhangsan@test.com"),
    ("李四", "lisi@test.com"),
    ("王五", "wangwu@test.com"),
    ("买家小赵", "zhao@test.com"),
    ("buyer_01", "b01@test.com"),
    ("buyer_02", "b02@test.com"),
    ("buyer_03", "b03@test.com"),
    ("buyer_04", "b04@test.com"),
    ("buyer_05", "b05@test.com"),
    ("buyer_06", "b06@test.com"),
]

# (name, description, price_yuan, stock, category)
PHONE = [
    ("iPhone 13 128G 午夜色", "95新，无划痕，电池健康89%，带原装充电器", 320000, 1, "电子产品"),
    ("iPhone 14 Pro 256G 暗紫色", "99新，激活仅一个月，配件齐全，保修到年底", 620000, 1, "电子产品"),
    ("华为 Mate 60 Pro 512G", "全新未拆封，雅丹黑，昆仑玻璃版", 699900, 2, "电子产品"),
    ("小米14 Ultra 16+512G", "9成新，拍照神器，徕卡光学镜头，送保护壳", 420000, 1, "电子产品"),
    ("三星 S24+ 256G", "国行在保，使用3个月，钴蓝配色，箱说全", 480000, 1, "电子产品"),
    ("一加 Ace 3 Pro 512G", "95新，性能怪兽，游戏流畅，超级闪充", 280000, 1, "电子产品"),
    ("iPhone 15 Pro Max 256G 原色钛金属", "99新，仅用两个月，AppleCare+到明年", 880000, 1, "电子产品"),
    ("vivo X100 Pro 512G 星迹蓝", "全新仅拆封验机，蔡司APO长焦，拍照旗舰", 399900, 3, "电子产品"),
    ("OPPO Find X7 Ultra 512G", "95新，双潜望长焦，哈苏人像，箱说全", 350000, 1, "电子产品"),
    ("荣耀 Magic6 Pro 512G 流云紫", "9成新，骁龙8Gen3，卫星通信，使用两个月", 480000, 1, "电子产品"),
]

BOOK = [
    ("《三体》全三册 精装版", "刘慈欣著，9成新，无折痕无笔记", 5800, 2, "图书音像"),
    ("《深入理解计算机系统》原书第3版", "CSAPP经典教材，8成新，部分章节有标注", 4500, 3, "图书音像"),
    ("《百年孤独》精装插图版", "马尔克斯经典，全新仅拆封，收藏级品相", 3900, 1, "图书音像"),
    ("《Python编程：从入门到实践》第3版", "95新，适合零基础入门，代码示例完整", 3500, 5, "图书音像"),
    ("《设计模式》英文原版", "GoF经典，9成新，计算机必读", 6800, 1, "图书音像"),
    ("《明朝那些事儿》全套9册", "当年明月著，8成新，历史入门佳作", 8800, 1, "图书音像"),
    ("《人类简史》+《未来简史》套装", "尤瓦尔·赫拉利，95新，社科入门经典", 6800, 3, "图书音像"),
    ("《活着》+《许三观卖血记》精装", "余华代表作套装，全新未拆", 3500, 4, "图书音像"),
    ("《算法导论》原书第4版", "MIT经典，9成新，少量荧光笔标注", 9900, 1, "图书音像"),
    ("《小王子》中英双语插图版", "全新，适合学英语，装帧精美", 2500, 6, "图书音像"),
    ("2025考研数学全套", "张宇30讲+1000题+真题，部分有笔记", 5800, 1, "图书音像"),
]

FURNITURE = [
    ("宜家 MALM 办公桌 140x65cm 白色", "使用一年，轻微使用痕迹，配件齐全", 35000, 1, "家具家居"),
    ("电竞椅 傲风C3 黑色", "使用半年，带头枕腰靠，搬家急出", 58000, 2, "家具家居"),
    ("北欧风实木书架 6层 橡木色", "尺寸180x80x30cm，承重好，9成新", 68000, 1, "家具家居"),
    ("折叠餐桌 宜家 NORDEN 桦木色", "可展开至152cm，适合小户型", 42000, 2, "家具家居"),
    ("乳胶床垫 1.8m×2m 20cm厚", "天然乳胶，软硬适中，仅用3个月", 78000, 1, "家具家居"),
    ("落地灯 简约北欧风 三档调光", "暖白光，金属灯杆+布艺灯罩", 8500, 4, "家具家居"),
    ("懒人沙发豆袋 加大号 深灰色", "填充饱满，可拆洗，躺下去不想起来", 16800, 3, "家具家居"),
    ("升降桌 双电机 140×70cm", "久坐族福音，站立办公，3档记忆", 128000, 1, "家具家居"),
    ("鞋柜 实木翻斗 三层 80cm宽", "门口收纳神器，原木色，9成新", 9800, 2, "家具家居"),
    ("全身镜 落地穿衣镜 170×50cm", "铝合金边框，防爆玻璃，全新", 5800, 5, "家具家居"),
]

CLOTH = [
    ("北面 1996 经典羽绒服 男L码", "黑色，正品，穿一季，保暖一流", 58000, 1, "服装鞋帽"),
    ("Nike Air Jordan 1 Low 倒钩 42码", "仅试穿，原盒原标，收藏自用皆宜", 128000, 1, "服装鞋帽"),
    ("优衣库 轻薄羽绒背心 女M码", "米白色，穿两次，轻便保暖", 8900, 3, "服装鞋帽"),
    ("Levi's 501 经典直筒牛仔裤 W32L32", "美产，养牛半年，已脱浆落色自然", 15800, 1, "服装鞋帽"),
    ("Arc'teryx Beta AR 冲锋衣 男XL码", "黑色GTX面料，防水透气，户外必备", 168000, 1, "服装鞋帽"),
    ("Nike Air Force 1 纯白 43码", "95新，经典百搭，鞋底轻微磨损", 32000, 2, "服装鞋帽"),
    ("Patagonia Retro-X 抓绒衣 男M码", "经典羊羔绒，保暖复古，穿两个月", 45000, 1, "服装鞋帽"),
    ("匡威 Chuck 70 高帮 黑色 42码", "全新仅试穿，经典款永不过时", 28900, 3, "服装鞋帽"),
    ("ZARA 羊毛混纺大衣 男L码 驼色", "穿三次，版型好，面料挺括", 19800, 1, "服装鞋帽"),
    ("Adidas Ultraboost 22 跑鞋 43码", "Boost中底，跑步通勤两用，9成新", 22000, 2, "服装鞋帽"),
]

ELEC = [
    ("戴森 V12 Detect Slim 无线吸尘器", "激光探测灰尘，使用半年，配件全", 168000, 1, "家用电器"),
    ("飞利浦空气炸锅 HD9650 XXL", "大容量，9成新，做过几次炸鸡", 38000, 2, "家用电器"),
    ("小米即热饮水机 S1", "3秒速热，多档温度，桌面款", 12800, 3, "家用电器"),
    ("石头扫地机器人 P10 Pro 扫拖一体", "自动集尘，用3个月，打扫干净省心", 158000, 1, "家用电器"),
    ("德龙全自动咖啡机 Magnifica S", "意式美式一键出品，定期除垢保养", 120000, 1, "家用电器"),
    ("华为路由器 AX6 Wi-Fi 6+", "7200Mbps，穿墙强，覆盖150平", 18500, 5, "家用电器"),
    ("美的变频空调 1.5匹 冷暖", "用两年，制冷制热快，节能省电", 128000, 1, "家用电器"),
    ("小熊电煮锅 多功能 1.5L", "煮面煮粥火锅一锅搞定，9成新", 4500, 4, "家用电器"),
    ("松下电饭煲 SR-DF101 3L", "IH加热，煮饭香糯，使用一年", 15800, 2, "家用电器"),
    ("小米空气净化器 4 Pro", "除甲醛除雾霾，适用60平米，用半年", 58000, 2, "家用电器"),
]

SPORTS = [
    ("迪卡侬山地自行车 ST100 26寸", "骑了半年，变速正常，送锁+灯", 32000, 1, "运动户外"),
    ("Keep 跑步机 K2 家用折叠", "仅用三个月，静音电机，App互联", 98000, 1, "运动户外"),
    ("迪卡侬哑铃组合 20kg 可调节", "铸铁包胶，几乎全新，练全身够用", 8800, 5, "运动户外"),
    ("YONEX 羽毛球拍 天斧99 Pro", "4U5G，穿了BG80线26磅，打两个月", 68000, 2, "运动户外"),
    ("帐篷 牧高笛 冷山3 三人帐", "双层防雨，露营用过两次，送地席", 15800, 3, "运动户外"),
    ("瑜伽垫 Liforme 天然橡胶 185cm", "专业防滑，厚度5mm，用了3个月", 12800, 4, "运动户外"),
    ("迪卡侬椭圆机 EL520 家用静音", "前驱14斤飞轮，8档阻力，App互联", 88000, 1, "运动户外"),
    ("游泳浮板 + 脚蹼套装", "Speedo正品，仅用一次游泳课", 3500, 3, "运动户外"),
]

DIGITAL = [
    ("iPad Air 5 256G 星光色 Wi-Fi版", "M1芯片，99新，配件齐全，有AppleCare", 420000, 1, "电子产品"),
    ("索尼 WH-1000XM5 降噪耳机 黑色", "头戴式降噪天花板，用两个月，箱说全", 168000, 2, "电子产品"),
    ("Apple Watch S9 45mm GPS版", "午夜色铝金属，95新，表带+充电器全", 198000, 1, "电子产品"),
    ("罗技 G Pro X Superlight 2 鼠标", "电竞无线鼠标，仅拆封试手感", 38000, 3, "电子产品"),
    ("机械键盘 Keychron K8 Pro 茶轴", "RGB背光，热插拔，铝框，用一个月", 19800, 4, "电子产品"),
    ("4K显示器 LG 27UK850 27寸 IPS", "Type-C 60W充电，设计剪辑利器，用一年", 168000, 1, "电子产品"),
    ("GoPro Hero 12 Black 运动相机", "5.3K视频，防水，配件全套，仅拍一次", 198000, 1, "电子产品"),
    ("Switch OLED 白色 + 塞尔达卡带3张", "99新，贴膜带壳，吃灰出", 158000, 1, "电子产品"),
    ("AirPods Pro 2 USB-C版", "用半年，降噪完美，耳机仓轻微划痕", 88000, 2, "电子产品"),
    ("Wacom 数位板 CTL-672 中号", "入门绘画板，仅用两次，送笔尖", 15800, 5, "电子产品"),
]

TOYS = [
    ("乐高 布加迪Chiron 科技旗舰 42083", "拼过一次即拆，零件齐全带说明书盒", 168000, 1, "其他"),
    ("乐高 机械组 兰博基尼 Sian 42115", "全新未拼，盒子完好，绝版涨价中", 198000, 1, "其他"),
    ("泡泡玛特 Molly 十二生肖系列 12盒", "全新未拆盒，一条端盒，不重复", 8888, 5, "其他"),
    ("万代 MG 高达 RX-78-2 3.0 素组", "已拼未涂装，水口处理干净，送支架", 8800, 3, "其他"),
    ("Switch 游戏卡带 王国之泪 + 奥德赛", "两张打包出，99新，插拔不超过五次", 16800, 2, "其他"),
]


def create_users(db):
    user_map = {}

    for username, email in MERCHANTS:
        exists = db.query(User).filter(User.username == username).first()
        if exists:
            user_map[username] = exists
            continue
        u = User(username=username, email=email,
                 hashed_password=security.get_password_hash(PASSWORD),
                 role=UserRole.MERCHANT, is_verified=True)
        db.add(u)
        db.flush()
        db.add(Wallet(user_id=u.id, balance=0))
        user_map[username] = u

    for username, email in BUYERS:
        exists = db.query(User).filter(User.username == username).first()
        if exists:
            user_map[username] = exists
            continue
        u = User(username=username, email=email,
                 hashed_password=security.get_password_hash(PASSWORD),
                 role=UserRole.USER, is_verified=True)
        db.add(u)
        db.flush()
        # 给买家预充值 100000 分 (1000 元)，方便测试
        wallet = Wallet(user_id=u.id, balance=10000000)
        db.add(wallet)
        db.add(Transaction(wallet_id=u.id, amount=10000000, type=TransactionType.RECHARGE,
                           description="新用户赠送体验金"))
        user_map[username] = u

    db.commit()
    return user_map


def create_products(db, user_map):
    # (merchant_key, product_list)
    mapping = [
        ("phone_m", PHONE),
        ("book_m", BOOK),
        ("furniture_m", FURNITURE),
        ("cloth_m", CLOTH),
        ("elec_m", ELEC),
        ("sports_m", SPORTS),
        ("digital_m", DIGITAL),
        ("toy_m", TOYS),
    ]

    total = 0
    for merchant_key, products in mapping:
        for i, (name, desc, price, stock, category) in enumerate(products):
            exists = db.query(Product).filter(Product.name == name).first()
            if exists:
                continue
            # 状态轮换：大部分 approved，少量其他
            if i == 0:
                status = ProductStatus.PENDING
            elif i == 1:
                status = ProductStatus.REJECTED
            elif i == len(products) - 1:
                status = ProductStatus.SOLD_OUT
            else:
                status = ProductStatus.APPROVED

            p = Product(
                name=name, description=desc, price=price, stock=stock,
                category=category, status=status,
                merchant_id=user_map[merchant_key].id,
                audit_remark=("描述与实际不符" if status == ProductStatus.REJECTED else None),
            )
            db.add(p)
            total += 1

    db.commit()
    return total


def main():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("  二手市场 — 大量测试数据生成器")
        print("=" * 60)

        # 管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(username="admin", email="admin@test.com",
                         hashed_password=security.get_password_hash("123"),
                         role=UserRole.ADMIN, is_verified=True)
            db.add(admin)
            db.flush()
            db.add(Wallet(user_id=admin.id, balance=0))
            print("\n  管理员: admin / 123")
        else:
            print("\n  管理员: admin (已存在)")

        user_map = create_users(db)
        merchant_count = sum(1 for u in user_map.values() if u.role == UserRole.MERCHANT)
        buyer_count = sum(1 for u in user_map.values() if u.role == UserRole.USER)
        print(f"\n  商家: {merchant_count} 个  |  买家: {buyer_count} 个")
        print(f"  所有测试账号密码: {PASSWORD}  |  买家初始余额: ¥10,000.00")

        count = create_products(db, user_map)
        print(f"\n  商品总数: {count} 件")
        for s in ProductStatus:
            c = db.query(Product).filter(Product.status == s).count()
            if c > 0:
                label = {"pending": "待审核", "approved": "已上架",
                         "rejected": "已拒绝", "sold_out": "已售罄"}[s.value]
                print(f"    {label}: {c} 件")

        from sqlalchemy import func
        cat_counts = db.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
        print(f"\n  分类分布:")
        for cat, cnt in sorted(cat_counts, key=lambda x: -x[1]):
            print(f"    {cat}: {cnt} 件")

        print(f"\n  管理端: http://localhost:5173/admin/login")
        print(f"  商家端: http://localhost:5173/merchant/login")
        print(f"  用户端: http://localhost:5173")
        print("=" * 60)

    except Exception as e:
        print(f"错误: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
