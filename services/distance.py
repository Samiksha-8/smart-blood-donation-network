from math import radians, sin, cos, sqrt, atan2


def calculate_distance(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate the distance between two geographical
    coordinates using the Haversine formula.

    Returns:
        Distance in kilometers.
    """

    if None in (
        latitude1,
        longitude1,
        latitude2,
        longitude2
    ):
        return None

    # Earth's radius in kilometers
    earth_radius = 6371.0

    lat1 = radians(latitude1)
    lon1 = radians(longitude1)

    lat2 = radians(latitude2)
    lon2 = radians(longitude2)

    difference_latitude = lat2 - lat1
    difference_longitude = lon2 - lon1

    a = (
        sin(difference_latitude / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(difference_longitude / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    distance = earth_radius * c

    return round(distance, 2)