from datasource.database import db


class UserEntity(db.Model):
    __tablename__ = "users"

    uuid = db.Column(db.String(36), primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
