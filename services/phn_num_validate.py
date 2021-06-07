import re


def mobile_number_check(mobile_number):
    """
    mobile_number
    params: mobile_number taken from customer and check it for validation
    return False/True
    """
    check = re.search(
        r"(^(?:\+88|88)?(01[3-9]\d{8})$)", mobile_number)

    if check is None:
        return False

    return True
