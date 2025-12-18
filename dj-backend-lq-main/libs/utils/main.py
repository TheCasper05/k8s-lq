import ssl


def cast_ssl_verify_mode(value):
    try:
        value_int = int(value)
        return ssl.VerifyMode(value_int)
    except ValueError:
        raise ValueError(f"Invalid value for ssl.VerifyMode: {value}")
    except Exception as e:
        raise e
