from datetime import datetime
from database.db import db


class DonationHistory(db.Model):
    __tablename__ = "donation_history"

    history_id = db.Column(
        db.Integer,
        primary_key=True
    )

    donor_id = db.Column(
        db.Integer,
        db.ForeignKey("donor_profiles.donor_id"),
        nullable=False
    )

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("blood_requests.request_id"),
        nullable=False
    )

    donation_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    units_donated = db.Column(
        db.Integer,
        default=1
    )