from datetime import datetime
from database.db import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(15), unique=True, nullable=False)

    role = db.Column(
        db.Enum("donor", "receiver", "admin"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    donor_profile = db.relationship(
        "DonorProfile",
        backref="user",
        uselist=False
    )