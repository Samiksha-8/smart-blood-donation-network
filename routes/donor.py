from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request,
    jsonify
)
from services.validation import (
    valid_person_name,
    valid_email,
    valid_city
)
from datetime import datetime
from models.donor import DonorProfile
from models.blood_request import BloodRequest
from models.donation_history import DonationHistory
from models.request_donor import RequestDonor
from models.user import User
from database.db import db
from services.eligibility import check_donor_eligibility
from services.recommendation import is_blood_compatible


donor_bp = Blueprint("donor", __name__, url_prefix="/donor")


# =========================================================
# DONOR DASHBOARD
# =========================================================

@donor_bp.route("/dashboard")
def dashboard():

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        flash("Donor profile not found.", "error")
        return redirect(url_for("auth.login"))

    # -----------------------------
    # CHECK DONOR ELIGIBILITY
    # -----------------------------

    eligible, reason = check_donor_eligibility(donor)

    # -----------------------------
    # FIND MATCHING REQUESTS
    # -----------------------------

    matching_requests = []

    if eligible:

        blood_requests = BloodRequest.query.filter(
            BloodRequest.status.in_(
                ["Pending", "Partially Fulfilled"]
            )
        ).order_by(
            BloodRequest.request_date.desc()
        ).all()

        for blood_request in blood_requests:

            # Check blood compatibility
            if not is_blood_compatible(
                blood_request.blood_group,
                donor.blood_group
            ):
                continue

            # Check whether donor already responded
            existing_response = RequestDonor.query.filter_by(
                request_id=blood_request.request_id,
                donor_id=donor.donor_id
            ).first()

            if existing_response:
                continue

            # Same city = nearby
            same_city = (
                donor.city.strip().lower()
                == blood_request.city.strip().lower()
            )

            matching_requests.append({
                "request": blood_request,
                "same_city": same_city
            })

        # Same city requests first
        matching_requests.sort(
            key=lambda item: not item["same_city"]
        )

    # -----------------------------
    # NEARBY COUNT
    # -----------------------------

    nearby_count = sum(
        1
        for item in matching_requests
        if item["same_city"]
    )

    # -----------------------------
    # RECENT DONATION HISTORY
    # -----------------------------

    recent_history = DonationHistory.query.filter_by(
        donor_id=donor.donor_id
    ).order_by(
        DonationHistory.donation_date.desc()
    ).limit(3).all()

    # -----------------------------
    # SEND DATA TO TEMPLATE
    # -----------------------------

    return render_template(
        "donor_dashboard.html",
        donor=donor,
        eligible=eligible,
        reason=reason,
        matching_requests=matching_requests[:3],
        nearby_count=nearby_count,
        recent_history=recent_history
    )

# =========================================================
# UPDATE DONOR AVAILABILITY
# =========================================================

@donor_bp.route("/availability", methods=["POST"])
def update_availability():

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        return jsonify({
            "success": False,
            "message": "Donor profile not found."
        }), 404

    data = request.get_json()

    donor.is_available = bool(data.get("is_available"))

    db.session.commit()

    return jsonify({
        "success": True,
        "is_available": donor.is_available
    })

# =========================================================
# DONOR BLOOD REQUESTS
# =========================================================

@donor_bp.route("/requests")
def requests():

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        flash("Donor profile not found.", "error")
        return redirect(url_for("donor.dashboard"))

    eligible, reason = check_donor_eligibility(donor)

    # If donor is not eligible, don't show requests
    if not eligible:

        return render_template(
            "donor_requests.html",
            donor=donor,
            requests_list=[],
            nearby_count=0,
            emergency_count=0,
            urgent_count=0,
            eligibility_message=reason
        )

    # Get active requests
    blood_requests = BloodRequest.query.filter(
        BloodRequest.status.in_(
            ["Pending", "Partially Fulfilled"]
        )
    ).order_by(
        BloodRequest.request_date.desc()
    ).all()

    matching_requests = []

    for blood_request in blood_requests:

        # Check blood group compatibility
        if not is_blood_compatible(
            blood_request.blood_group,
            donor.blood_group
        ):
            continue

        # Check whether donor already responded
        response = RequestDonor.query.filter_by(
            request_id=blood_request.request_id,
            donor_id=donor.donor_id
        ).first()

        if response:
            continue

        # Same city = nearby for now
        same_city = (
            donor.city.strip().lower()
            == blood_request.city.strip().lower()
        )

        matching_requests.append({
            "request": blood_request,
            "same_city": same_city,
            "response": None
        })

    # Same city requests first
    matching_requests.sort(
        key=lambda item: not item["same_city"]
    )

    nearby_count = sum(
        1
        for item in matching_requests
        if item["same_city"]
    )

    emergency_count = sum(
        1
        for item in matching_requests
        if item["request"].urgency == "Emergency"
    )

    urgent_count = sum(
        1
        for item in matching_requests
        if item["request"].urgency == "Urgent"
    )

    return render_template(
        "donor_requests.html",
        donor=donor,
        requests_list=matching_requests,
        nearby_count=nearby_count,
        emergency_count=emergency_count,
        urgent_count=urgent_count,
        eligibility_message=None
    )


# =========================================================
# VIEW SINGLE BLOOD REQUEST
# =========================================================

@donor_bp.route("/request/<int:request_id>")
def view_request(request_id):

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        flash("Donor profile not found.", "error")
        return redirect(url_for("donor.dashboard"))

    blood_request = BloodRequest.query.filter_by(
        request_id=request_id
    ).first()

    if not blood_request:
        flash("Blood request not found.", "error")
        return redirect(url_for("donor.requests"))

    # Check whether this request matches donor's blood group
    if not is_blood_compatible(
        blood_request.blood_group,
        donor.blood_group
    ):
        flash("This blood request does not match your blood group.", "error")
        return redirect(url_for("donor.requests"))

    eligible, reason = check_donor_eligibility(donor)

    response = RequestDonor.query.filter_by(
        request_id=request_id,
        donor_id=donor.donor_id
    ).first()

    return render_template(
        "donor_request_details.html",
        donor=donor,
        blood_request=blood_request,
        eligible=eligible,
        reason=reason,
        response=response
    )


# =========================================================
# ACCEPT BLOOD REQUEST
# =========================================================

@donor_bp.route("/request/<int:request_id>/accept", methods=["POST"])
def accept_request(request_id):

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        flash("Donor profile not found.", "error")
        return redirect(url_for("donor.dashboard"))

    blood_request = BloodRequest.query.filter_by(
        request_id=request_id
    ).first()

    if not blood_request:
        flash("Blood request not found.", "error")
        return redirect(url_for("donor.requests"))

    if blood_request.status not in ["Pending", "Partially Fulfilled"]:
        flash("This blood request is no longer active.", "error")
        return redirect(url_for("donor.requests"))

    # Check donor eligibility
    eligible, reason = check_donor_eligibility(donor)

    if not eligible:
        flash(reason, "error")
        return redirect(url_for("donor.requests"))

    # Check blood compatibility
    if not is_blood_compatible(
        blood_request.blood_group,
        donor.blood_group
    ):
        flash("This request does not match your blood group.", "error")
        return redirect(url_for("donor.requests"))

    # Prevent duplicate response
    existing = RequestDonor.query.filter_by(
        request_id=request_id,
        donor_id=donor.donor_id
    ).first()

    if existing:
        flash("You have already responded to this request.", "error")
        return redirect(url_for(
            "donor.view_request",
            request_id=request_id
        ))

    # Create donor response
    response = RequestDonor(
        request_id=request_id,
        donor_id=donor.donor_id,
        status="Accepted",
        response_time=datetime.utcnow()
    )

    db.session.add(response)
    db.session.commit()

    flash("You have accepted the blood request.", "success")

    return redirect(url_for("donor.requests"))


# =========================================================
# REJECT BLOOD REQUEST
# =========================================================

@donor_bp.route("/request/<int:request_id>/reject", methods=["POST"])
def reject_request(request_id):

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        flash("Donor profile not found.", "error")
        return redirect(url_for("donor.dashboard"))

    blood_request = BloodRequest.query.filter_by(
        request_id=request_id
    ).first()

    if not blood_request:
        flash("Blood request not found.", "error")
        return redirect(url_for("donor.requests"))

    if blood_request.status not in ["Pending", "Partially Fulfilled"]:
        flash("This blood request is no longer active.", "error")
        return redirect(url_for("donor.requests"))

    # Check whether donor already responded
    existing = RequestDonor.query.filter_by(
        request_id=request_id,
        donor_id=donor.donor_id
    ).first()

    if existing:
        flash("You have already responded to this request.", "error")
        return redirect(url_for(
            "donor.view_request",
            request_id=request_id
        ))

    # Create rejection response
    response = RequestDonor(
        request_id=request_id,
        donor_id=donor.donor_id,
        status="Rejected"
    )

    db.session.add(response)
    db.session.commit()

    flash("You have rejected the blood request.", "success")

    return redirect(url_for("donor.requests"))


# =========================================================
# DONATION HISTORY
# =========================================================

@donor_bp.route("/history")
def donation_history():

    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    donor = DonorProfile.query.filter_by(
        user_id=donor_user_id
    ).first()

    if not donor:
        flash("Donor profile not found.", "error")
        return redirect(url_for("donor.dashboard"))

    history = DonationHistory.query.filter_by(
        donor_id=donor.donor_id
    ).order_by(
        DonationHistory.donation_date.desc()
    ).all()

    if history:
        donor.last_donation_date = history[0].donation_date.date()

    db.session.commit()

    return render_template(
        "donation_history.html",
        donor=donor,
        history=history
    )

@donor_bp.route("/profile", methods=["GET", "POST"])
def profile():
    donor_user_id = session.get("user_id")

    if not donor_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(user_id=donor_user_id).first()
    donor = DonorProfile.query.filter_by(user_id=donor_user_id).first()

    if not user or not donor:
        flash("Profile not found.", "error")
        return redirect(url_for("donor.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        weight_string = request.form.get("weight", "").strip()

        if not full_name or not email or not phone or not city or not weight_string:
            flash("Please fill all profile fields.", "error")
            return redirect(url_for("donor.profile"))

        if not valid_person_name(full_name):
            flash("Please enter a valid name without numbers.", "error")
            return redirect(url_for("donor.profile"))

        if not valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("donor.profile"))

        existing_email = User.query.filter(
            User.email == email,
            User.user_id != user.user_id,
        ).first()
        if existing_email:
            flash("This email is already registered.", "error")
            return redirect(url_for("donor.profile"))

        if not valid_city(city):
            flash("Please enter a valid city name without numbers.", "error")
            return redirect(url_for("donor.profile"))

        try:
            weight = float(weight_string)
        except (TypeError, ValueError):
            flash("Please enter a valid weight.", "error")
            return redirect(url_for("donor.profile"))

        if not 50 <= weight <= 300:
            flash("Weight must be between 50 kg and 300 kg.", "error")
            return redirect(url_for("donor.profile"))

        user.full_name = full_name
        user.email = email
        user.phone = phone  # No phone-number format validation added.
        donor.city = city
        donor.weight = weight

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print("Donor profile update error:", error)
            flash("Could not update your profile. Please try again.", "error")
            return redirect(url_for("donor.profile"))

        session["user_name"] = user.full_name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("donor.profile"))

    return render_template("donor_profile.html", user=user, donor=donor)
