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
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.COOKIES.get('token')

        request.user = None
        if token:
            try:
                decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user = User.objects.get(id=decoded.get('userId'))
                request.user = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
                return JsonResponse({'error': 'Invalid or expired token.'}, status=403)

        return self.get_response(request)
