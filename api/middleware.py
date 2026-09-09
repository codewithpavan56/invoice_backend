import jwt
from django.conf import settings
from django.http import JsonResponse
from api.models import User

JWT_SECRET = 'ultrakey_jwt_secret_token_key_12345'

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1].strip()
            else:
                token = auth_header.strip()
        
        if not token:
            token = request.COOKIES.get('token')

        request.user = None
        if token:
            try:
                decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = decoded.get('userId') or decoded.get('id') or decoded.get('user_id')
                if user_id:
                    request.user = User.objects.filter(id=user_id).first()
            except Exception:
                # Do not block request here for stale/invalid tokens.
                # If an endpoint requires auth, @require_auth decorator will handle returning 401.
                request.user = None

        return self.get_response(request)
