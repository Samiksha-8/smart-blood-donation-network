from datetime import date, datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import db
from models.user import User
from models.donor import DonorProfile
from services.validation import (
    valid_person_name,
    valid_email,
    valid_city,
    age_on_date,
    VALID_BLOOD_GROUPS,
    VALID_GENDERS,
)


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Account information
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    selected_role = request.form.get("role", "").strip().lower()

    # Required account fields. Phone format validation is intentionally not added.
    if not full_name or not email or not phone:
        flash("Please fill in all required account information.", "error")
        return redirect(url_for("auth.register"))

    if not password:
        flash("Please enter a password.", "error")
        return redirect(url_for("auth.register"))

    if not valid_person_name(full_name):
        flash(
            "Name must contain only letters, spaces, apostrophes, periods or hyphens.",
            "error",
        )
        return redirect(url_for("auth.register"))

    if not valid_email(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("auth.register"))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("auth.register"))

    # Frontend roles: donor / recipient. Database role for recipient: receiver.
    if selected_role == "donor":
        role = "donor"
    elif selected_role == "recipient":
        role = "receiver"
    else:
        flash("Please select Blood Donor or Blood Recipient.", "error")
        return redirect(url_for("auth.register"))

    # Duplicate email check
    if User.query.filter_by(email=email).first():
        flash("An account with this email already exists.", "error")
        return redirect(url_for("auth.register"))

    # Preserve existing duplicate-phone check; no phone-format validation is performed.
    if User.query.filter_by(phone=phone).first():
        flash("An account with this phone number already exists.", "error")
        return redirect(url_for("auth.register"))

    # Collect and validate donor details before saving the account.
    donor_values = None
    if role == "donor":
        blood_group = request.form.get("blood_group", "").strip()
        city = request.form.get("city", "").strip()
        date_of_birth_string = request.form.get("date_of_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        weight_string = request.form.get("weight", "").strip()
        last_donation_string = request.form.get("last_donation_date", "").strip()
        is_available = request.form.get("available") == "on"

        if not blood_group or not city or not date_of_birth_string or not gender or not weight_string:
            flash("Please complete all required donor information.", "error")
            return redirect(url_for("auth.register"))

        if blood_group not in VALID_BLOOD_GROUPS:
            flash("Please select a valid blood group.", "error")
            return redirect(url_for("auth.register"))

        if not valid_city(city):
            flash("Please enter a valid city name without numbers.", "error")
            return redirect(url_for("auth.register"))

        if gender not in VALID_GENDERS:
            flash("Please select a valid gender.", "error")
            return redirect(url_for("auth.register"))

        try:
            date_of_birth = datetime.strptime(date_of_birth_string, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date of birth.", "error")
            return redirect(url_for("auth.register"))

        if date_of_birth > date.today():
            flash("Date of birth cannot be in the future.", "error")
            return redirect(url_for("auth.register"))

        if age_on_date(date_of_birth) < 18:
            flash("Donors must be at least 18 years old.", "error")
            return redirect(url_for("auth.register"))

        try:
            weight = float(weight_string)
        except (TypeError, ValueError):
            flash("Please enter a valid weight.", "error")
            return redirect(url_for("auth.register"))

        if not 50 <= weight <= 300:
            flash("Weight must be between 50 kg and 300 kg.", "error")
            return redirect(url_for("auth.register"))

        last_donation_date = None
        if last_donation_string:
            try:
                last_donation_date = datetime.strptime(
                    last_donation_string, "%Y-%m-%d"
                ).date()
            except ValueError:
                flash("Invalid last donation date.", "error")
                return redirect(url_for("auth.register"))

            if last_donation_date > date.today():
                flash("Last donation date cannot be in the future.", "error")
                return redirect(url_for("auth.register"))

            if last_donation_date < date_of_birth:
                flash("Last donation date cannot be before your date of birth.", "error")
                return redirect(url_for("auth.register"))

        donor_values = {
            "blood_group": blood_group,
            "city": city,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "weight": weight,
            "last_donation_date": last_donation_date,
            "is_available": is_available,
        }

    # Create user and, if applicable, donor profile in one transaction.
    try:
        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            phone=phone,
            role=role,
        )
        db.session.add(new_user)
        db.session.flush()  # Obtain user_id before creating donor profile.

        if donor_values is not None:
            donor_profile = DonorProfile(
                user_id=new_user.user_id,
                blood_group=donor_values["blood_group"],
                date_of_birth=donor_values["date_of_birth"],
                gender=donor_values["gender"],
                weight=donor_values["weight"],
                city=donor_values["city"],
                last_donation_date=donor_values["last_donation_date"],
                is_available=donor_values["is_available"],
            )
            db.session.add(donor_profile)

        db.session.commit()
    except Exception as error:
        db.session.rollback()
        print("Registration error:", error)
        flash("Something went wrong while creating your account.", "error")
        return redirect(url_for("auth.register"))

    flash("Account created successfully. Please sign in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Please enter your email and password.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if user is None or not check_password_hash(user.password, password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login"))

    session["user_id"] = user.user_id
    session["user_role"] = user.role
    session["user_name"] = user.full_name

    if request.form.get("remember") == "on":
        session.permanent = True
    else:
        session.permanent = False

    if user.role == "donor":
        return redirect(url_for("donor.dashboard"))

    if user.role == "receiver":
        return redirect(url_for("receiver.dashboard"))

    if user.role == "admin":
        flash("Admin dashboard is not available yet.", "error")
        session.clear()
        return redirect(url_for("auth.login"))

    session.clear()
    flash("Invalid account role.", "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
