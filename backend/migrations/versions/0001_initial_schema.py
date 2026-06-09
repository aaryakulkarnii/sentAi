"""Initial schema – all SentinelAI entity tables.

Revision ID: 0001
Revises:
Create Date: 2026-06-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="tier1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "mitre_techniques",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("tactic", sa.String(length=100), nullable=False),
        sa.Column("technique", sa.String(length=200), nullable=False),
        sa.Column("sub_technique", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mitigation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=False),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("os", sa.String(length=100), nullable=True),
        sa.Column("criticality", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "detection_rules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("mitre_technique_id", sa.String(length=20), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["mitre_technique_id"], ["mitre_techniques.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("rule_id", sa.String(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("source_ip", sa.String(length=45), nullable=True),
        sa.Column("dest_ip", sa.String(length=45), nullable=True),
        sa.Column("host_id", sa.String(), nullable=True),
        sa.Column("raw_event_id", sa.String(length=255), nullable=True),
        sa.Column("mitre_technique_id", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["mitre_technique_id"], ["mitre_techniques.id"]),
        sa.ForeignKeyConstraint(["rule_id"], ["detection_rules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assigned_to", sa.String(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "incident_alerts",
        sa.Column("incident_id", sa.String(), nullable=False),
        sa.Column("alert_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("incident_id", "alert_id"),
    )

    op.create_table(
        "incident_notes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("incident_id", sa.String(), nullable=False),
        sa.Column("author_id", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "investigations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("incident_id", sa.String(), nullable=False),
        sa.Column("agent_output", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("attack_timeline", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("mitre_mappings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("iocs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("remediation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("incident_id", sa.String(), nullable=False),
        sa.Column("format", sa.String(length=10), nullable=False),
        sa.Column("s3_key", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("investigations")
    op.drop_table("incident_notes")
    op.drop_table("incident_alerts")
    op.drop_table("incidents")
    op.drop_table("alerts")
    op.drop_table("detection_rules")
    op.drop_table("assets")
    op.drop_table("mitre_techniques")
    op.drop_table("users")
