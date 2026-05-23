from django.urls import path
from .views import *

urlpatterns = [
    path('api/v1/signup/', Signup.as_view(), name='signup'),
    path('api/v1/signin/', Signin.as_view(), name='signin'),
    path('api/v1/vpn-usage/<str:username>/', UserVolumeStatus.as_view(), name='vpn_volume_status'),
]