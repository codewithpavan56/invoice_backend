from django.urls import path, include
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("Server is working Fine")

urlpatterns = [
    path('', health_check),
    path('api/', include('api.urls')),
]
