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
        msg = "Request processed successfully"
        if isinstance(data, dict) and "msg" in data:
            msg = data["msg"]
            # Remove msg from actual_data if it got injected there
            if isinstance(actual_data, list) and len(actual_data) > 0 and isinstance(actual_data[0], dict) and "msg" in actual_data[0]:
                actual_data[0].pop("msg", None)

        response = {
            "status": "success" if status_code < 400 else "failure",
            "msg": msg,
            "statuscode": status_code,
            "data": actual_data if isinstance(actual_data, list) else [actual_data],
            "meta": meta
        }

        return super().render(response, accepted_media_type, renderer_context)
