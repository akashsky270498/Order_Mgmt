import json
from .models import AuditLog

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We need to capture the payload before the view consumes it, 
        # but request.body can only be read once. So we decode it, though we don't log sensitive info.
        payload = ''
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Limit size to avoid huge payloads
                if len(request.body) < 10000:
                    payload = request.body.decode('utf-8')
                    # Basic sanitization for audit log
                    if 'password' in payload:
                        payload = '{"hidden": "contains sensitive data"}'
            except Exception:
                pass

        response = self.get_response(request)

        # Log it asynchronously or synchronously (synchronous for simplicity here)
        if request.path.startswith('/api/'):
            user = request.user if request.user.is_authenticated else None
            ip_address = request.META.get('REMOTE_ADDR')
            
            AuditLog.objects.create(
                user=user,
                method=request.method,
                path=request.path,
                ip_address=ip_address,
                status_code=response.status_code,
                payload=payload
            )

        return response
