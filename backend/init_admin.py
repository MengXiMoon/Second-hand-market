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
            print("密码: 123")
            return
        
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=security.get_password_hash("123"),
            role=UserRole.ADMIN,
            is_verified=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("管理员账号创建成功！")
        print("用户名: admin")
        print("密码: 123")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
