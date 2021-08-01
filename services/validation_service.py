def validate_server_data(attrs):
    if "owner" in attrs and len(attrs.get("owner")) < 1:
        return "title field is required"
    elif "server" in attrs and len(attrs["server"]) < 0:
        return "server field is required"
    elif "address" in attrs and len(attrs["address"]) > 0:
        return "address field is required"
    else:
        return True


# Schedule validations
def validate_schedule_data(data):
    if "name" in data and len(data.get("name")) < 1:
        return "name field is required"
