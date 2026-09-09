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
        
        # 1. Authorization header (Bearer or raw token)
        auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1].strip()
            else:
                token = auth_header.strip()
        
        # 2. Custom header
        if not token:
            token = request.headers.get('x-access-token') or request.headers.get('X-Access-Token')

        # 3. Cookies
        if not token:
            token = request.COOKIES.get('token') or request.COOKIES.get('jwt') or request.COOKIES.get('accessToken')

        # 4. Query string
        if not token:
            token = request.GET.get('token') or request.GET.get('auth') or request.GET.get('accessToken')

        request.user = None
        if token:
            try:
                decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = decoded.get('userId') or decoded.get('id') or decoded.get('user_id') or decoded.get('sub')
                if user_id:
                    request.user = User.objects.filter(id=user_id).first()
            except Exception:
                request.user = None

        return self.get_response(request)
