def validate_requirements_data(attrs):
    if "title" in attrs and len(attrs.get("title")) < 1:
        return "title field is required"
    elif "options" in attrs and len(attrs["options"]) > 0:
        options = attrs.get("options")
        for option in options:
            if option.get("name", None) is None or option.get("price") is None:
                return "Provide valid options value"
    else:
        return "Please provide valid options"
