from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from django.utils.translation import gettext_lazy as _

class CustomJWTAuthentication(JWTAuthentication):
    def get_raw_token(self, header):
        """
        Extracts the raw token string from the given "Authorization" header value.
        Allows "Bearer <token>", "JWT <token>", or just "<token>" directly.
        """
        parts = header.split()

        if len(parts) == 0:
            return None

        # Resolve header types to bytes for matching (e.g. [b'Bearer', b'JWT'])
        allowed_types = [
            t.encode('utf-8') if isinstance(t, str) else t
            for t in api_settings.AUTH_HEADER_TYPES
        ]

        # Standard check: if it has two parts and the first is one of the AUTH_HEADER_TYPES (e.g. Bearer)
        if len(parts) == 2:
            if parts[0] in allowed_types:
                return parts[1]
            
        # If it is a single part, or the prefix did not match but it looks like a JWT token (3 dot-separated parts)
        token_candidate = parts[0] if len(parts) == 1 else parts[1]
        
        if isinstance(token_candidate, bytes):
            token_str = token_candidate.decode('utf-8', errors='ignore')
        else:
            token_str = str(token_candidate)
            
        # JWT tokens consist of three parts (header, payload, signature) separated by dots
        if token_str.count('.') == 2:
            return token_candidate

        # Fallback to standard behavior
        return super().get_raw_token(header)
