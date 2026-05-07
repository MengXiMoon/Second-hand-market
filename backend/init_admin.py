import secrets

from app.db.session import SessionLocal
from app.models.models import User, UserRole
from app.core import security


def init_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("管理员账号已存在")
            print(f"用户名: admin")
            print("密码: CKSCGlZiruc")
            return

        password = secrets.token_urlsafe(8)
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=security.get_password_hash(password),
            role=UserRole.ADMIN,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("管理员账号创建成功！")
        print("=" * 50)
        print(f"  用户名: admin")
        print(f"  密码:   {password}")
        print("=" * 50)
        print("请妥善保管此密码。可通过环境变量 ADMIN_INIT_PASSWORD 指定初始密码。")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import os
    # Allow explicit override via environment variable
    override = os.getenv("ADMIN_INIT_PASSWORD")
    if override:
        # Monkey-patch secrets.token_urlsafe to return the override
        secrets.token_urlsafe = lambda n: override
    init_admin()
