from django.urls import path
from .views import *

urlpatterns = [
    path('api/v1/signup/', Signup.as_view(), name='signup'),
    path('api/v1/signin/', Signin.as_view(), name='signin'),
    path('api/v1/vpn-usage/<str:username>/', UserVolumeStatus.as_view(), name='vpn_volume_status'),
    # 🌟 Updated paths to extract the username directly from the URL route parameter
    path('api/v1/user-profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),

    path('api/v1/devices/update-usage/', UpdateDeviceUsageView.as_view(), name='update_device_usage'),
    path('api/v1/devices/toggle-block/', ToggleBlockDeviceView.as_view(), name='toggle_block_device'),

    # 🌟 2. GENERIC VARIABLE PATHS LAST
    path('api/v1/devices/<str:username>/', DeviceSessionView.as_view(), name='device_sessions'),

]