from rest_framework.exceptions import ValidationError


def get_plain_error_message(ex):
    """
    Accepts an exception object and returns a plain string error message.
    Handles DRF ValidationError and other exception types.
    """
    if isinstance(ex, ValidationError):
        messages = []
        errors = ex.detail

        if isinstance(errors, dict):
            for field_errors in errors.values():
                if isinstance(field_errors, list):
                    messages.extend(str(err) for err in field_errors)
                else:
                    messages.append(str(field_errors))
        elif isinstance(errors, list):
            messages.extend(str(err) for err in errors)
        else:
            messages.append(str(errors))

        return " ".join(messages)

    return str(ex)


def get_serializer_plain_error_msg(ex):
    """
    Converts DRF ValidationError or any exception into a plain text message.
    Adds field name before message like 'title may not be blank.'
    """
    if isinstance(ex, ValidationError):
        messages = []
        errors = ex.detail

        if isinstance(errors, dict):
            for field, field_errors in errors.items():
                if isinstance(field_errors, list):
                    for err in field_errors:
                        messages.append(f"{field} {err}")
                else:
                    messages.append(f"{field} {field_errors}")

        elif isinstance(errors, list):
            messages.extend(str(err) for err in errors)

        else:
            messages.append(str(errors))
        return " ".join(messages)
    return str(ex)

