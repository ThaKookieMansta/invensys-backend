"""03_01_26:Added org details tables and relationships in user and laptop details

Revision ID: 407008f5636a
Revises: 498a12568a95
Create Date: 2026-01-03 09:15:04.558397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '407008f5636a'
down_revision: Union[str, Sequence[str], None] = '498a12568a95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # =====================================================
    # 1. Create master tables
    # =====================================================

    op.create_table(
        "is_businessunit",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("unit_name", sa.String(), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
        ),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "is_department",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("department_name", sa.String(), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
        ),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
    )

    # =====================================================
    # 2. Seed master tables from existing STRING data
    # =====================================================

    op.execute("""
        INSERT INTO is_businessunit (unit_name)
        SELECT DISTINCT business_unit
        FROM is_user
        WHERE business_unit IS NOT NULL
        ON CONFLICT (unit_name) DO NOTHING
    """)

    op.execute("""
        INSERT INTO is_businessunit (unit_name)
        SELECT DISTINCT business_unit
        FROM is_laptopdetail
        WHERE business_unit IS NOT NULL
        ON CONFLICT (unit_name) DO NOTHING
    """)

    op.execute("""
        INSERT INTO is_department (department_name)
        SELECT DISTINCT department
        FROM is_user
        WHERE department IS NOT NULL
        ON CONFLICT (department_name) DO NOTHING
    """)

    # =====================================================
    # 3. Add new UUID FK columns (nullable for now)
    # =====================================================

    op.add_column(
        "is_user",
        sa.Column(
            "business_unit_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.add_column(
        "is_user",
        sa.Column(
            "department_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.add_column(
        "is_laptopdetail",
        sa.Column(
            "business_unit_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # =====================================================
    # 4. Backfill FK columns from old STRING columns
    # =====================================================

    op.execute("""
        UPDATE is_user u
        SET business_unit_id = b.id
        FROM is_businessunit b
        WHERE u.business_unit = b.unit_name
    """)

    op.execute("""
        UPDATE is_user u
        SET department_id = d.id
        FROM is_department d
        WHERE u.department = d.department_name
    """)

    op.execute("""
        UPDATE is_laptopdetail l
        SET business_unit_id = b.id
        FROM is_businessunit b
        WHERE l.business_unit = b.unit_name
    """)

    # =====================================================
    # 5. Convert modified_at from STRING → DATETIME
    # =====================================================

    op.alter_column(
        "is_user",
        "modified_at",
        type_=sa.DateTime(),
        postgresql_using="modified_at::timestamp",
    )

    # =====================================================
    # 6. Drop old STRING columns
    # =====================================================

    op.drop_column("is_user", "business_unit")
    op.drop_column("is_user", "department")
    op.drop_column("is_laptopdetail", "business_unit")

    # =====================================================
    # 7. Add foreign key constraints (LAST)
    # =====================================================

    op.create_foreign_key(
        "fk_user_business_unit",
        "is_user",
        "is_businessunit",
        ["business_unit_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_user_department",
        "is_user",
        "is_department",
        ["department_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_laptop_business_unit",
        "is_laptopdetail",
        "is_businessunit",
        ["business_unit_id"],
        ["id"],
    )


def downgrade():
    # =====================================================
    # Reverse FK constraints
    # =====================================================

    op.drop_constraint("fk_laptop_business_unit", "is_laptopdetail",
                       type_="foreignkey")
    op.drop_constraint("fk_user_department", "is_user", type_="foreignkey")
    op.drop_constraint("fk_user_business_unit", "is_user", type_="foreignkey")

    # =====================================================
    # Recreate old STRING columns
    # =====================================================

    op.add_column("is_user",
                  sa.Column("business_unit", sa.String(), nullable=True))
    op.add_column("is_user",
                  sa.Column("department", sa.String(), nullable=True))
    op.add_column("is_laptopdetail",
                  sa.Column("business_unit", sa.String(), nullable=True))

    # =====================================================
    # Backfill STRING columns from FK tables
    # =====================================================

    op.execute("""
        UPDATE is_user u
        SET business_unit = b.unit_name
        FROM is_businessunit b
        WHERE u.business_unit_id = b.id
    """)

    op.execute("""
        UPDATE is_user u
        SET department = d.department_name
        FROM is_department d
        WHERE u.department_id = d.id
    """)

    op.execute("""
        UPDATE is_laptopdetail l
        SET business_unit = b.unit_name
        FROM is_businessunit b
        WHERE l.business_unit_id = b.id
    """)

    # =====================================================
    # Drop FK columns
    # =====================================================

    op.drop_column("is_laptopdetail", "business_unit_id")
    op.drop_column("is_user", "department_id")
    op.drop_column("is_user", "business_unit_id")

    # =====================================================
    # Revert modified_at
    # =====================================================

    op.alter_column(
        "is_user",
        "modified_at",
        type_=sa.String(),
        postgresql_using="modified_at::text",
    )

    # =====================================================
    # Drop master tables
    # =====================================================

    op.drop_table("is_department")
    op.drop_table("is_businessunit")
