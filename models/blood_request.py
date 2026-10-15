from datetime import datetime
from database.db import db


class BloodRequest(db.Model):
    __tablename__ = "blood_requests"

    request_id = db.Column(db.Integer, primary_key=True)

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    blood_group = db.Column(
        db.String(5),
        nullable=False
    )

    units_required = db.Column(
        db.Integer,
        nullable=False
    )

    hospital_name = db.Column(
        db.String(150),
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )
    message = db.Column(db.Text)
 
    urgency = db.Column(
        db.Enum("Normal", "Urgent", "Emergency"),
        default="Normal"
    )

    status = db.Column(
        db.Enum(
            "Pending",
            "Partially Fulfilled",
            "Completed",
            "Cancelled"
        ),
        default="Pending"
    )

    request_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )