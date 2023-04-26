"""Auto generated

Revision ID: 53a93f17a53d
Revises: 4c4cb56442a9
Create Date: 2023-04-25 18:46:59.742398

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "53a93f17a53d"
down_revision = "4c4cb56442a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("messages_queue_id_fkey", "messages", type_="foreignkey")
    op.create_foreign_key(None, "messages", "queues", ["queue_id"], ["id"], ondelete="CASCADE")
    op.drop_constraint("queues_topic_id_fkey", "queues", type_="foreignkey")
    op.drop_constraint("queues_dead_queue_id_fkey", "queues", type_="foreignkey")
    op.create_foreign_key(None, "queues", "topics", ["topic_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(None, "queues", "queues", ["dead_queue_id"], ["id"], ondelete="SET NULL")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "queues", type_="foreignkey")
    op.drop_constraint(None, "queues", type_="foreignkey")
    op.create_foreign_key("queues_dead_queue_id_fkey", "queues", "queues", ["dead_queue_id"], ["id"])
    op.create_foreign_key("queues_topic_id_fkey", "queues", "topics", ["topic_id"], ["id"])
    op.drop_constraint(None, "messages", type_="foreignkey")
    op.create_foreign_key("messages_queue_id_fkey", "messages", "queues", ["queue_id"], ["id"])
    # ### end Alembic commands ###