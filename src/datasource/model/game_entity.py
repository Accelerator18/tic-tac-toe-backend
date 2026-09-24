from datetime import datetime, UTC

from datasource.database import db


class GameEntity(db.Model):
    __tablename__ = "games"

    uuid = db.Column(db.String(36), primary_key=True)
    board = db.Column(db.JSON, nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), nullable=False)

    player_x_uuid = db.Column(db.String(36), db.ForeignKey("users.uuid"), nullable=False)
    player_o_uuid = db.Column(db.String(36), db.ForeignKey("users.uuid"), nullable=True)
    current_turn_uuid = db.Column(db.String(36), db.ForeignKey("users.uuid"), nullable=True)
    winner_uuid = db.Column(db.String(36), db.ForeignKey("users.uuid"), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
