from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    EditProfileView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='get-profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit-profile'),
]