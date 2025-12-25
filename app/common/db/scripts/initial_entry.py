import asyncio

from bcrypt import gensalt, hashpw
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import engine
from app.modules.jobs.models.jobs import *  # noqa: F403
from app.modules.users.models.admin import Admin, AdminRole
from app.modules.users.models.user import *  # noqa: F403


async def create_admin_user():
    admin_email = "algorithmicdev9@gmail.com"
    admin_password = "algodev@9"
    admin_role = AdminRole.SUPER_ADMIN

    async with AsyncSession(engine) as session:
        try:
            # Check if admin already exists
            result = await session.exec(select(Admin).where(Admin.email == admin_email))
            existing = result.first()

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
            await session.commit()
            print("Admin user created successfully.")
        except Exception as e:
            print(f"Error creating admin user: {e}")


async def main():
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())
