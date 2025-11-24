from datetime import datetime
from sqlmodel import Session, select
from app.db.config import engine
from app.db.models.user import Users, Role
from app.db.models.jobs import Job
from bcrypt import hashpw, gensalt


def create_admin_user():
    admin_email = "algorithmicdev9@gmail.com"
    admin_username = "admin"
    admin_password = "vivek@123"
    admin_role = Role.ADMIN

    with Session(engine) as session:
        try:
            # Check if admin already exists
            existing = session.exec(select(Users).where(Users.username == admin_username)).first()
            if existing:
                print("Admin user already exists.")
                return

            hashed_password = hashpw(admin_password.encode("utf-8"), gensalt()).decode("utf-8")
            admin_user = Users(
                first_name="Admin",
                last_name="Account",
                email=admin_email,
                username=admin_username,
                password=hashed_password,
                role=admin_role,
                refresh_token=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
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