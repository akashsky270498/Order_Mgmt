from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        
        # Check if the data is already properly formatted (e.g., from our custom Exception Handler)
        if isinstance(data, dict) and 'status' in data and 'statuscode' in data:
            return super().render(data, accepted_media_type, renderer_context)

        # Handle Paginated Responses (DRF pagination adds 'results')
        if isinstance(data, dict) and 'results' in data:
            meta = {
                "count": data.get("count"),
                "next": data.get("next"),
                "previous": data.get("previous")
            }
            actual_data = data.get("results", [])
        else:
            meta = data.get("meta", {}) if isinstance(data, dict) else {}
            # Ensure data is always an array as per requirement
            if isinstance(data, dict):
                if "data" in data:
                    actual_data = data["data"]
                else:
                    actual_data = [data]
            elif isinstance(data, list):
                actual_data = data
            else:
                actual_data = [data] if data is not None else []

        # Get custom message if provided from the view, otherwise set a sensible default
        msg = None
        if isinstance(data, dict) and "msg" in data:
            msg = data["msg"]
        else:
            # Try to infer a friendly message from the view, request and HTTP method
            try:
                view = renderer_context.get('view')
                request = renderer_context.get('request')
                method = request.method if request is not None else None

                # Helper: infer resource name
                resource = None
                if view is not None:
                    qs = getattr(view, 'queryset', None)
                    if qs is not None and hasattr(qs, 'model'):
                        resource = qs.model.__name__
                    elif hasattr(view, 'serializer_class') and view.serializer_class is not None:
                        ser = view.serializer_class
                        if hasattr(ser, 'Meta') and hasattr(ser.Meta, 'model'):
                            resource = ser.Meta.model.__name__

                path = request.path if request is not None else ''

                view_name = view.__class__.__name__ if view is not None else ''

                # Special-case common endpoints
                if 'register' in path or 'Register' in view_name:
                    msg = "User registered successfully."
                elif 'login' in path or 'token' in path or 'TokenObtainPairView' in view_name:
                    msg = "User logged in successfully."
                elif 'profile' in path or 'Profile' in view_name:
                    msg = "Profile fetched successfully." if method == 'GET' else "Profile updated successfully."
                elif 'orders' in path or 'Order' in view_name:
                    if method == 'POST':
                        msg = "Order placed successfully. Payment processing initiated asynchronously."
                    elif method == 'PATCH' or method == 'PUT':
                        msg = "Order updated successfully."
                    else:
                        msg = "Orders fetched successfully."
                elif 'products' in path or 'Product' in view_name or resource == 'Product':
                    if method == 'POST':
                        msg = "Product created successfully."
                    elif method in ('PATCH', 'PUT'):
                        msg = "Product updated successfully."
                    elif method == 'DELETE':
                        msg = "Product deleted successfully."
                    else:
                        msg = "Products fetched successfully."
                else:
                    # Generic method-based messages with optional resource name
                    verb = None
                    if method == 'GET':
                        verb = 'fetched'
                    elif method == 'POST':
                        verb = 'created'
                    elif method in ('PATCH', 'PUT'):
                        verb = 'updated'
                    elif method == 'DELETE':
                        verb = 'deleted'
                    if resource:
                        msg = f"{resource} {verb} successfully." if verb else "Request processed successfully"
                    else:
                        msg = f"Request processed successfully" if msg is None else msg
            except Exception:
                msg = "Request processed successfully"
            # Remove msg from actual_data if it got injected there
            if isinstance(actual_data, list) and len(actual_data) > 0 and isinstance(actual_data[0], dict) and "msg" in actual_data[0]:
                actual_data[0] = actual_data[0].copy()
                actual_data[0].pop("msg", None)

        response = {
            "status": "success" if status_code < 400 else "failure",
            "msg": msg,
            "statuscode": status_code,
            "data": actual_data if isinstance(actual_data, list) else [actual_data],
            "meta": meta
        }

        return super().render(response, accepted_media_type, renderer_context)
