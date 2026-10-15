from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from database.db import db
from models.blood_request import BloodRequest
from models.donor import DonorProfile
from models.user import User
from models.request_donor import RequestDonor
from datetime import datetime
from models.donation_history import DonationHistory
from services.eligibility import check_donor_eligibility
from services.recommendation import get_compatible_blood_groups


receiver_bp = Blueprint("receiver", __name__)


@receiver_bp.route("/recipient/dashboard")
def dashboard():

    receiver_id = session.get("user_id")

    if not receiver_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    requests_list = BloodRequest.query.filter_by(
        receiver_id=receiver_id
    ).order_by(
        BloodRequest.request_date.desc()
    ).all()

    active_requests = BloodRequest.query.filter(
        BloodRequest.receiver_id == receiver_id,
        BloodRequest.status.in_(["Pending", "Partially Fulfilled"])
    ).count()

    latest_request = requests_list[0] if requests_list else None

    fulfilled_units = 0
    nearby_donors = 0

    if latest_request:

        donations = DonationHistory.query.filter_by(
            request_id=latest_request.request_id
        ).all()

        fulfilled_units = sum(
            donation.units_donated
            for donation in donations
        )

        compatible_groups = get_compatible_blood_groups(
            latest_request.blood_group
        )

        donors = DonorProfile.query.filter(
            DonorProfile.blood_group.in_(compatible_groups)
        ).all()

        for donor in donors:

            eligible, reason = check_donor_eligibility(donor)

            if not eligible:
                continue

            same_city = (
                donor.city.strip().lower()
                == latest_request.city.strip().lower()
            )

            if same_city:
                nearby_donors += 1

    return render_template(
        "recipient_dashboard.html",
        user_name=session.get("user_name"),
        active_requests=active_requests,
        latest_request=latest_request,
        fulfilled_units=fulfilled_units,
        nearby_donors=nearby_donors
    )


@receiver_bp.route("/recipient/create-request", methods=["GET", "POST"])
def create_request():

    if request.method == "POST":

        receiver_id = session.get("user_id")

        if not receiver_id:
            flash("Please login first.", "error")
            return redirect(url_for("auth.login"))

        blood_group = request.form.get("blood_group")
        units = request.form.get("units")
        hospital_name = request.form.get("hospital")
        city = request.form.get("city")
        urgency = request.form.get("urgency")
        message = request.form.get("message")

        if units == "5+":
            units_required = 5
        else:
            units_required = int(units)

        urgency_map = {
            "normal": "Normal",
            "urgent": "Urgent",
            "emergency": "Emergency"
        }

        urgency_value = urgency_map.get(urgency)

        new_request = BloodRequest(
            receiver_id=receiver_id,
            blood_group=blood_group,
            units_required=units_required,
            hospital_name=hospital_name,
            city=city,
            urgency=urgency_value,
            message=message,
            status="Pending"
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Blood request created successfully!", "success")

        return redirect(
            url_for(
                "receiver.find_donors",
                request_id=new_request.request_id
            )
        )

    return render_template("create_request.html")


@receiver_bp.route("/recipient/requests")
def my_requests():

    receiver_id = session.get("user_id")

    if not receiver_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    requests_list = BloodRequest.query.filter_by(
        receiver_id=receiver_id
    ).order_by(
        BloodRequest.request_date.desc()
    ).all()

    return render_template(
        "recipient_requests.html",
        requests_list=requests_list
    )


@receiver_bp.route("/recipient/find-donors")
def find_donors():

    receiver_id = session.get("user_id")

    if not receiver_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    request_id = request.args.get("request_id", type=int)
    expand_search = request.args.get("expanded") == "1"

    if request_id:
        blood_request = BloodRequest.query.filter_by(
            request_id=request_id,
            receiver_id=receiver_id
        ).first()
    else:
        blood_request = BloodRequest.query.filter_by(
            receiver_id=receiver_id
        ).order_by(
            BloodRequest.request_date.desc()
        ).first()

    if not blood_request:
        flash("Please create a blood request first.", "error")
        return redirect(url_for("receiver.create_request"))

    compatible_groups = get_compatible_blood_groups(
        blood_request.blood_group
    )

    donors = DonorProfile.query.filter(
        DonorProfile.blood_group.in_(compatible_groups)
    ).all()

    eligible_donors = []

    for donor in donors:

        is_eligible, reason = check_donor_eligibility(donor)

        if not is_eligible:
            continue

        same_city = (
            donor.city.strip().lower()
            == blood_request.city.strip().lower()
        )

        donor_user = User.query.get(donor.user_id)

        eligible_donors.append({
            "donor": donor,
            "user": donor_user,
            "same_city": same_city
        })

    # Same-city donors first
    eligible_donors.sort(key=lambda item: not item["same_city"])

    # Default search shows only same-city donors
    if not expand_search:
        eligible_donors = [
            item for item in eligible_donors
            if item["same_city"]
        ]

    return render_template(
        "find_donors.html",
        blood_request=blood_request,
        donors=eligible_donors,
        expand_search=expand_search,
        user_name=session.get("user_name")
    )

@receiver_bp.route("/recipient/request/<int:request_id>")
def request_details(request_id):

    receiver_id = session.get("user_id")

    if not receiver_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    blood_request = BloodRequest.query.filter_by(
        request_id=request_id,
        receiver_id=receiver_id
    ).first()

    if not blood_request:
        flash("Request not found.", "error")
        return redirect(url_for("receiver.my_requests"))

    accepted_responses = RequestDonor.query.filter_by(
        request_id=request_id,
        status="Accepted"
    ).all()

    accepted_donors = []

    for response in accepted_responses:

        donor = DonorProfile.query.filter_by(
            donor_id=response.donor_id
        ).first()

        if donor:

            user = User.query.filter_by(
                user_id=donor.user_id
            ).first()

            accepted_donors.append({
                "response": response,
                "donor": donor,
                "user": user
            })

    return render_template(
        "recipient_request_details.html",
        blood_request=blood_request,
        accepted_donors=accepted_donors
    )

@receiver_bp.route("/recipient/request/<int:request_id>/donate/<int:donor_id>", methods=["POST"])
def record_donation(request_id, donor_id):

    receiver_id = session.get("user_id")

    if not receiver_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    # Make sure this request belongs to this recipient
    blood_request = BloodRequest.query.filter_by(
        request_id=request_id,
        receiver_id=receiver_id
    ).first()

    if not blood_request:
        flash("Request not found.", "error")
        return redirect(url_for("receiver.dashboard"))

    # Make sure this donor accepted the request
    response = RequestDonor.query.filter_by(
        request_id=request_id,
        donor_id=donor_id,
        status="Accepted"
    ).first()

    if not response:
        flash("This donor has not accepted the request.", "error")
        return redirect(
            url_for("receiver.request_details", request_id=request_id)
        )

    # Prevent duplicate donation record
    existing_donation = DonationHistory.query.filter_by(
        donor_id=donor_id,
        request_id=request_id
    ).first()

    if existing_donation:
        flash("Donation has already been recorded.", "error")
        return redirect(
            url_for("receiver.request_details", request_id=request_id)
        )

    # Units donated
    units_donated = 1

    donation = DonationHistory(
        donor_id=donor_id,
        request_id=request_id,
        donation_date=datetime.utcnow().date(),
        units_donated=units_donated
    )

    db.session.add(donation)

    donor = DonorProfile.query.filter_by(
        donor_id=donor_id
    ).first()

    if donor:
        donor.last_donation_date = donation.donation_date

    db.session.flush()

    total_units = db.session.query(
        db.func.sum(DonationHistory.units_donated)
    ).filter_by(
        request_id=request_id
    ).scalar() or 0

    if total_units >= blood_request.units_required:
        blood_request.status = "Completed"
    else:
        blood_request.status = "Partially Fulfilled"

    db.session.commit()

    flash("Donation recorded successfully!", "success")

    return redirect(
        url_for(
            "receiver.request_details",
            request_id=request_id
        )
    )
@receiver_bp.route("/recipient/profile", methods=["GET", "POST"])
def profile():

    receiver_id = session.get("user_id")

    if not receiver_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(user_id=receiver_id).first()

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("receiver.dashboard"))

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not full_name or not email or not phone:
            flash("Please fill all profile fields.", "error")
            return redirect(url_for("receiver.profile"))

        user.full_name = full_name
        user.email = email
        user.phone = phone

        db.session.commit()

        # Update session name so dashboard immediately shows new name
        session["user_name"] = user.full_name

        flash("Profile updated successfully!", "success")

        return redirect(url_for("receiver.profile"))

    return render_template(
        "recipient_profile.html",
        user=user
    )