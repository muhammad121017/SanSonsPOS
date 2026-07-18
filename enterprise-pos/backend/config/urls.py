from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': {'username': user.username, 'id': user.id, 'role': 'Admin' if user.is_superuser else 'Cashier'}})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    username = request.data.get('username')
    password = request.data.get('password')
    is_admin = request.data.get('is_admin', False)

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    if is_admin:
        user.is_superuser = True
        user.is_staff = True
        user.save()

    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'message': 'User created successfully.',
        'token': token.key,
        'user': {'username': user.username, 'id': user.id, 'role': 'Admin' if user.is_superuser else 'Cashier'}
    }, status=status.HTTP_201_CREATED)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', custom_login, name='api_token_auth'),
    path('api/auth/register/', register_user, name='register_user'), 
    path('api/inventory/', include('inventory.urls')),
    
    # This force-serves static files when DEBUG=False
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]