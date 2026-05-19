from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first, to get the standard error response
    response = exception_handler(exc, context)

    status_code = 500
    msg = "An unexpected error occurred"
    data = []

    if response is not None:
        status_code = response.status_code
        # Flatten DRF error dictionaries (e.g., {"email": ["This field is required."]})
        if isinstance(response.data, dict):
            if "detail" in response.data:
                msg = response.data["detail"]
            else:
                # Combine validation error messages into a single readable string
                errors = []
                for key, value in response.data.items():
                    if isinstance(value, list):
                        errors.append(f"{key}: {', '.join([str(v) for v in value])}")
                    else:
                        errors.append(f"{key}: {str(value)}")
                msg = "Validation Error: " + " | ".join(errors)
        elif isinstance(response.data, list):
            msg = str(response.data[0])

    elif isinstance(exc, ValidationError):
        status_code = 400
        msg = f"Validation Error: {str(exc.message)}"
    else:
        msg = str(exc)

    # Construct the exact failure format requested
    custom_response = {
        "status": "failure",
        "msg": msg,
        "statuscode": status_code,
        "data": data,
        "meta": {}
    }

    if response is not None:
        response.data = custom_response
    else:
        # If it was an unhandled exception, create a response object
        from rest_framework.response import Response
        response = Response(custom_response, status=status_code)

    return response
