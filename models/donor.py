from database.db import db


class DonorProfile(db.Model):
    __tablename__ = "donor_profiles"

    donor_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False,
        unique=True                # one user one donor profile
    )

    blood_group = db.Column(db.String(5), nullable=False)

    date_of_birth = db.Column(db.Date, nullable=False)

    gender = db.Column(db.String(10), nullable=False)

    weight = db.Column(db.Float, nullable=False)

    city = db.Column(db.String(100), nullable=False)

    last_donation_date = db.Column(db.Date)

    is_available = db.Column(
        db.Boolean,
        default=True
    )

