from datetime import datetime
from database.db import db


class RequestDonor(db.Model):
    __tablename__ = "request_donors"

    id = db.Column(db.Integer, primary_key=True)

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("blood_requests.request_id"),
        nullable=False
    )

    donor_id = db.Column(
        db.Integer,
        db.ForeignKey("donor_profiles.donor_id"),
        nullable=False
    )

    status = db.Column(
        db.Enum(
            "Pending",
            "Accepted",
            "Rejected",
            "Expired"
        ),
        default="Pending"
    )

    response_time = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )