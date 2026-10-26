
import re
from datetime import date


VALID_BLOOD_GROUPS = {
    "A+", "A-", "B+", "B-",
    "AB+", "AB-", "O+", "O-"
}

VALID_GENDERS = {"Male", "Female", "Other"}


def valid_person_name(value):
    value = (value or "").strip()

    if not 2 <= len(value) <= 100:
        return False

    # Letters only, with spaces and common name separators.
    # Reject numbers, underscores and other symbols.
    return bool(
        re.fullmatch(
            r"[^\W\d_]+(?:[ .'-][^\W\d_]+)*",
            value,
            re.UNICODE
        )
    )


def valid_email(value):
    value = (value or "").strip()

    if not value or len(value) > 254 or ".." in value:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
            r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",
            value
        )
    )


def valid_city(value):
    value = (value or "").strip()

    if not 2 <= len(value) <= 100:
        return False

    return bool(
        re.fullmatch(
            r"[^\W\d_]+(?:[ .,'-][^\W\d_]+)*",
            value,
            re.UNICODE
        )
    )


def valid_hospital_name(value):
    value = (value or "").strip()

    if not 2 <= len(value) <= 150:
        return False

    if not any(char.isalpha() for char in value):
        return False

    return bool(
        re.fullmatch(
            r"[^\W\d_][\w .,'()&/#-]*",
            value,
            re.UNICODE
        )
    )


def parse_iso_date(value):
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def age_on_date(dob, today=None):
    if not dob:
        return None

    today = today or date.today()

    return (
        today.year - dob.year
        - ((today.month, today.day) < (dob.month, dob.day))
    )
