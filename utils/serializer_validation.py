def serialize_errors(errors):
    plain_text_errors = []
    for field, error_list in errors.items():
        for error in error_list:
            plain_text_errors.append(f"{field}: {error}")
    return "\n".join(plain_text_errors)

