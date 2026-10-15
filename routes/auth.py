from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.db import db
from models.user import User
from models.donor import DonorProfile


auth_bp = Blueprint("auth", __name__)


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    # -------------------------------
    # Display registration page
    # -------------------------------

    if request.method == "GET":
        return render_template("register.html")


    # -------------------------------
    # Get account information
    # -------------------------------

    full_name = request.form.get(
        "full_name", ""
    ).strip()

    email = request.form.get(
        "email", ""
    ).strip().lower()

    phone = request.form.get(
        "phone", ""
    ).strip()

    password = request.form.get(
        "password", ""
    )

    confirm_password = request.form.get(
        "confirm_password", ""
    )

    selected_role = request.form.get(
        "role", ""
    ).strip().lower()


    # -------------------------------
    # Validate basic information
    # -------------------------------

    if not full_name or not email or not phone:
        flash(
            "Please fill in all required account information.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    if not password:
        flash(
            "Please enter a password.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # -------------------------------
    # Validate passwords
    # -------------------------------

    if password != confirm_password:
        flash(
            "Passwords do not match.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # -------------------------------
    # Convert frontend role
    #
    # HTML:
    # donor
    # recipient
    #
    # Database:
    # donor
    # receiver
    # -------------------------------

    if selected_role == "donor":

        role = "donor"

    elif selected_role == "recipient":

        role = "receiver"

    else:

        flash(
            "Please select Blood Donor or Blood Recipient.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # -------------------------------
    # Check duplicate email
    # -------------------------------

    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email:

        flash(
            "An account with this email already exists.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # -------------------------------
    # Check duplicate phone
    # -------------------------------

    existing_phone = User.query.filter_by(
        phone=phone
    ).first()

    if existing_phone:

        flash(
            "An account with this phone number already exists.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # =====================================================
    # CREATE USER
    # =====================================================

    new_user = User(
        full_name=full_name,
        email=email,
        password=generate_password_hash(password),
        phone=phone,
        role=role
    )

    db.session.add(new_user)

    # Get generated user_id before creating donor profile
    db.session.flush()


    # =====================================================
    # CREATE DONOR PROFILE
    # =====================================================

    if role == "donor":

        blood_group = request.form.get(
            "blood_group", ""
        ).strip()

        city = request.form.get(
            "city", ""
        ).strip()

        date_of_birth_string = request.form.get(
            "date_of_birth", ""
        ).strip()

        gender = request.form.get(
            "gender", ""
        ).strip()

        weight_string = request.form.get(
            "weight", ""
        ).strip()

        last_donation_string = request.form.get(
            "last_donation_date", ""
        ).strip()

        is_available = (
            request.form.get("available") == "on"
        )


        # -------------------------------
        # Validate donor information
        # -------------------------------

        if not blood_group or not city:

            db.session.rollback()

            flash(
                "Blood group and city are required for donors.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        if not date_of_birth_string:

            db.session.rollback()

            flash(
                "Date of birth is required for donors.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        if not gender:

            db.session.rollback()

            flash(
                "Please select your gender.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        if not weight_string:

            db.session.rollback()

            flash(
                "Weight is required for donors.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # -------------------------------
        # Convert date of birth
        # -------------------------------

        try:

            date_of_birth = datetime.strptime(
                date_of_birth_string,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            db.session.rollback()

            flash(
                "Invalid date of birth.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # -------------------------------
        # Convert weight
        # -------------------------------

        try:

            weight = float(weight_string)

        except ValueError:

            db.session.rollback()

            flash(
                "Please enter a valid weight.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        if weight <= 0:

            db.session.rollback()

            flash(
                "Weight must be greater than zero.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # -------------------------------
        # Convert last donation date
        # -------------------------------

        last_donation_date = None

        if last_donation_string:

            try:

                last_donation_date = datetime.strptime(
                    last_donation_string,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                db.session.rollback()

                flash(
                    "Invalid last donation date.",
                    "error"
                )

                return redirect(
                    url_for("auth.register")
                )


        # -------------------------------
        # Create donor profile
        # -------------------------------

        donor_profile = DonorProfile(
            user_id=new_user.user_id,
            blood_group=blood_group,
            date_of_birth=date_of_birth,
            gender=gender,
            weight=weight,
            city=city,
            last_donation_date=last_donation_date,
            is_available=is_available
        )

        db.session.add(donor_profile)


    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    try:

        db.session.commit()

    except Exception as error:

        db.session.rollback()

        print("Registration error:", error)

        flash(
            "Something went wrong while creating your account.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # =====================================================
    # SUCCESS
    # =====================================================

    flash(
        "Account created successfully. Please sign in.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # -----------------------------------------
    # Show login page
    # -----------------------------------------

    if request.method == "GET":
        return render_template("login.html")


    # -----------------------------------------
    # Get login information
    # -----------------------------------------

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )


    # -----------------------------------------
    # Basic validation
    # -----------------------------------------

    if not email or not password:

        flash(
            "Please enter your email and password.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------
    # Find user
    # -----------------------------------------

    user = User.query.filter_by(
        email=email
    ).first()


    # -----------------------------------------
    # Check user + password
    # -----------------------------------------

    if user is None or not check_password_hash(
        user.password,
        password
    ):

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # -----------------------------------------
    # Create login session
    # -----------------------------------------

    session["user_id"] = user.user_id
    session["user_role"] = user.role
    session["user_name"] = user.full_name


    # -----------------------------------------
    # Remember me
    # -----------------------------------------

    if request.form.get("remember") == "on":

        session.permanent = True

    else:

        session.permanent = False


    # -----------------------------------------
    # Redirect according to role
    # -----------------------------------------

    if user.role == "donor":

        return redirect(
            url_for("donor.dashboard")
        )


    if user.role == "receiver":

        return redirect(
            url_for("receiver.dashboard")
        )


    if user.role == "admin":

        # Admin route will be implemented later.
        flash(
            "Admin dashboard is not available yet.",
            "error"
        )

        session.clear()

        return redirect(
            url_for("auth.login")
        )


    # Safety fallback

    session.clear()

    flash(
        "Invalid account role.",
        "error"
    )

    return redirect(
        url_for("auth.login")
    )

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))