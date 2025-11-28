from bcrypt import gensalt, hashpw
from sqlmodel import Session, select

from app.common.db.config import engine
from app.modules.users.models.admin import Admin, AdminRole


def create_admin_user():
    admin_email = "vivekgupta@gmail.com"
    admin_password = "vivek@123"
    admin_role = AdminRole.SUPER_ADMIN

    with Session(engine) as session:
        try:
            # Check if admin already exists
            existing = session.exec(select(Admin).where(Admin.email == admin_email)).first()

            if existing:
                print("Admin user already exists.")
                return

            hashed_password = hashpw(admin_password.encode("utf-8"), gensalt()).decode("utf-8")
            admin_user = Admin(
                first_name="Vivek",
                last_name="Gupta",
                email=admin_email,
                password=hashed_password,
                role=admin_role,
                refresh_token=None,
            )
            session.add(admin_user)
            session.commit()
            print("Admin user created successfully.")
        except Exception as e:
            print(f"Error creating admin user: {e}")


def main():
    create_admin_user()


if __name__ == "__main__":
    main()
