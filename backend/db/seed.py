import logging
from os.path import exists

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.sessions import AsyncSessionLocal, engine
from db.models.is_users import User
# from db.models.is_roles import Role
from db.models.is_laptop_status import LaptopStatus
from db.models.is_laptop_details import LaptopDetail
from datetime import datetime
from core.hashing import Hasher
from core.logging_config import logger



async def safe_seed_data():
    async with AsyncSessionLocal() as session:
        logger.info("Checking for seed data")
        result = await session.execute(select(User).limit(1))
        user = result.scalar()
        if not user:
            logger.info("🚀 Seeding initial data...")
            await seed_data(session)
            logger.info("✅ Seeding complete.")
        else:
            logger.info("⚡ Data already exists, skipping seeding.")



async def seed_data(session):
        # roles = ["Admin", "IT Support", "Employee"]
        # for r in roles:
        #     exists = await session.scalar(select(Role).where(Role.name == r))
        #     if not exists:
        #         session.add(Role(name=r))

        statuses = ["Available", "Allocated", "Under Repair", "Retired", "Lost"]
        for s in statuses:
            exists = await session.scalar(select(LaptopStatus).where(LaptopStatus.status_name == s))
            if not exists:
                session.add(LaptopStatus(status_name=s))

        users = [
            {
                "first_name": "Invensys",
                "last_name": "Admin",
                "username": "admin",
                "email_address": "is_admin@moev.co.ke",
                "password": "Password@1",
                "superuser": True
            }
        ]

        for u in users:
            exists = await session.scalar(select(User).where(User.username == u["username"]))
            if not exists:
                admin_user = User(
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    username=u["username"],
                    email_address=u["email_address"],
                    password_hash=Hasher.hash_password(u["password"]),
                    is_superuser=u["superuser"],

                )
                session.add(admin_user)
                await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_data())
