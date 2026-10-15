# Blood group compatibility rules
# Key = recipient blood group
# Value = blood groups that can donate to that recipient

COMPATIBLE_BLOOD_GROUPS = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"]
}


def get_compatible_blood_groups(recipient_blood_group):
    """
    Return blood groups that can donate to the recipient.
    """
    return COMPATIBLE_BLOOD_GROUPS.get(
        recipient_blood_group,
        []
    )


def is_blood_compatible(
    recipient_blood_group,
    donor_blood_group
):
    """
    Check whether a donor's blood group is compatible
    with the recipient.
    """
    compatible_groups = get_compatible_blood_groups(
        recipient_blood_group
    )

    return donor_blood_group in compatible_groups