from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError

def custom_exception_handler(exc, context):
    try:
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
                    msg = str(response.data["detail"])
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
            else:
                msg = str(response.data)

        elif isinstance(exc, ValidationError):
            status_code = 400
            if hasattr(exc, 'message_dict'):
                msg = "Validation Error: " + " | ".join([f"{k}: {', '.join(v)}" for k, v in exc.message_dict.items()])
            elif hasattr(exc, 'messages'):
                msg = "Validation Error: " + " | ".join(exc.messages)
            else:
                msg = f"Validation Error: {str(exc)}"
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
    except Exception as e:
        # Fallback if the exception handler itself throws an exception
        from rest_framework.response import Response
        return Response({
            "status": "failure",
            "msg": f"An unexpected system error occurred: {str(e)}",
            "statuscode": 500,
            "data": [],
            "meta": {}
        }, status=500)
