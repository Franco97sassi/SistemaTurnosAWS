"""Create turnos table."""
from alembic import op
import sqlalchemy as sa

revision = "20260915_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "turnos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cliente", sa.String(100), nullable=False),
        sa.Column("servicio", sa.String(100), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="pendiente"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("estado IN ('pendiente', 'cancelado')", name="ck_turnos_estado"),
    )
    for column in ("cliente", "servicio", "fecha", "estado"):
        op.create_index(f"ix_turnos_{column}", "turnos", [column])


def downgrade():
    op.drop_table("turnos")
