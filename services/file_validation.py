import base64


def image_to_base64(image):
    try:
        encoded_string = base64.b64encode(image.read())
        base64_str = encoded_string.decode('utf-8')
        return base64_str
    except Exception as e:
        return str(e)


def is_base64(base_64):
    """
    valid base64 checking
    params base64
    return True/False
    """
    try:
        if len(base_64) == 0:
            return False

        if isinstance(base_64, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(base_64, 'ascii')
        elif isinstance(base_64, bytes):
            sb_bytes = base_64
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes

    except Exception as e:
        print(e)
        return False


def is_pdf_file(base_64):
    """ valid base64 to pdf checking
    params base64
    return True/False
    """

    try:
        if len(base_64) == 0:
            return False

        else:
            pdf_bytes = base64.b64decode(base_64, validate=True)
            if pdf_bytes[0:4] == b'%PDF':
                return True

    except Exception as e:
        print(e)
        return False
