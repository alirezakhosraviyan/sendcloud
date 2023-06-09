"""init database

Revision ID: 0a1f01ac20d6
Revises:
Create Date: 2023-06-06 01:04:07.831233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0a1f01ac20d6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "feeds",
        sa.Column("pk", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("link", sa.VARCHAR(length=512), nullable=False),
        sa.Column("title", sa.VARCHAR(length=255), nullable=False),
        sa.Column("lang", sa.VARCHAR(length=30), nullable=False),
        sa.Column("copyright_text", sa.VARCHAR(length=5000), nullable=False),
        sa.Column("description", sa.VARCHAR(length=5000), nullable=False),
        sa.Column("category", sa.VARCHAR(length=255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("link"),
    )
    op.create_index(op.f("ix_feeds_pk"), "feeds", ["pk"], unique=False)
    op.create_table(
        "users",
        sa.Column("pk", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.VARCHAR(length=255), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_pk"), "users", ["pk"], unique=False)
    op.create_table(
        "postings",
        sa.Column("pk", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("link", sa.VARCHAR(length=512), nullable=False),
        sa.Column("title", sa.VARCHAR(length=255), nullable=False),
        sa.Column("description", sa.VARCHAR(length=5000), nullable=False),
        sa.Column("author", sa.VARCHAR(length=3000), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("feed_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["feed_id"],
            ["feeds.pk"],
        ),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("link"),
    )
    op.create_index(op.f("ix_postings_pk"), "postings", ["pk"], unique=False)
    op.create_table(
        "user_feed",
        sa.Column("feed_pk", sa.Integer(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["feed_pk"],
            ["feeds.pk"],
        ),
        sa.ForeignKeyConstraint(
            ["user_pk"],
            ["users.pk"],
        ),
        sa.PrimaryKeyConstraint("feed_pk", "user_pk"),
    )
    op.create_table(
        "read_postings",
        sa.Column("posting_pk", sa.Integer(), nullable=False),
        sa.Column("user_pk", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["posting_pk"],
            ["postings.pk"],
        ),
        sa.ForeignKeyConstraint(
            ["user_pk"],
            ["users.pk"],
        ),
        sa.PrimaryKeyConstraint("posting_pk", "user_pk"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("read_postings")
    op.drop_table("user_feed")
    op.drop_index(op.f("ix_postings_pk"), table_name="postings")
    op.drop_table("postings")
    op.drop_index(op.f("ix_users_pk"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_feeds_pk"), table_name="feeds")
    op.drop_table("feeds")
    # ### end Alembic commands ###
