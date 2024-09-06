from utils import messages


def prepare_create_success_response(message):
    """ prepare success response for all serializer """
    response = {
        'status': 'success',
        'message': message
    }
    return response


def prepare_success_response(message):
    """ prepare success response for all serializer """
    response = {
        'status': 'success',
        'message': message
    }
    return response


def prepare_single_success_response(data):
    """Prepare single success response"""
    response = {
        'status': 'success',
        'message': messages.DATA_RETURN,
        'data': data
    }
    return response


def prepare_success_list_response(message, data):
    """ prepare success response for all serializer """
    response = {
        'status': 'success',
        'message': message,
        'data': data
    }
    return response


def prepare_error_response(serializer_error):
    """ prepare error response for all serializer """
    response = {
        'status': 'fail',
        'message': serializer_error,
    }
    return response


def signin_success_response(user_id, fullname, email, role, role_name, device_token, token):
    response = {
        'status': 'success',
        'message': messages.SIGNIN_SUCCESS,
        'user_id': user_id,
        'fullname': fullname,
        'email': email,
        'role': role,
        'role_name': role_name,
        'token': token,
        'device_token': device_token,
    }
    return response


def prepare_company_home_response(sliders, package):
    response = {
        'status': 'success',
        'message': messages.DATA_RETURN,
        'sliders': sliders,
        'packages': package,
    }
    return response


def company_transition_response(total_sales, total_ticket, total_income, sliders=None):
    response = {
        'status': 'success',
        'message': messages.DATA_RETURN,
        'total_sales_event': total_sales,
        'total_sales_ticket': total_ticket,
        'total_income': total_income,
        'sliders': sliders,
    }
    return response
