"""Guarantee one active appointment per time slot."""

from alembic import op

revision = "20260915_02"
down_revision = "20260915_01"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE UNIQUE INDEX uq_turnos_fecha_pendiente "
        "ON turnos (fecha) WHERE estado = 'pendiente'"
    )


def downgrade():
    op.drop_index("uq_turnos_fecha_pendiente", table_name="turnos")
