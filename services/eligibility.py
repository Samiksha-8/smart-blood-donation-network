from datetime import date, timedelta


# Waiting period after a donation.
# This can be changed later if your project uses
# a different medical/academic rule.
DONATION_WAITING_DAYS = 90


def calculate_age(date_of_birth):
    """
    Calculate the donor's current age.
    """

    if not date_of_birth:
        return None

    today = date.today()

    age = today.year - date_of_birth.year

    if (today.month, today.day) < (
        date_of_birth.month,
        date_of_birth.day
    ):
        age -= 1

    return age


def is_donation_waiting_period_over(last_donation_date):
    """
    Check whether the donor has completed the
    required waiting period after their last donation.

    Returns:
        True  -> donor can be considered
        False -> donor is still in waiting period
    """

    if not last_donation_date:
        return True

    days_since_donation = (
        date.today() - last_donation_date
    ).days

    return days_since_donation >= DONATION_WAITING_DAYS


def check_donor_eligibility(donor):
    if not donor.is_available:
        return False, "Donor is currently unavailable"

    age = calculate_age(donor.date_of_birth)

    if age is None:
        return False, "Date of birth is missing"

    if age < 18:
        return False, "Donor must be at least 18 years old"

    if donor.weight is None:
        return False, "Weight information is missing"

    if donor.weight < 50:
        return False, "Donor does not meet minimum weight requirement"

    if donor.last_donation_date:
        next_donation_date = (
            donor.last_donation_date
            + timedelta(days=DONATION_WAITING_DAYS)
        )

        if not is_donation_waiting_period_over(
            donor.last_donation_date
        ):
            return False, (
                f"Donor is in the donation waiting period. "
                f"Next eligible date: "
                f"{next_donation_date.strftime('%d %b %Y')}."
            )

    return True, "Donor is eligible"