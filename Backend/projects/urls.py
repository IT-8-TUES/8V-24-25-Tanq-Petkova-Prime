from django.urls import path
from .views import CreateFirmFromURLView

urlpatterns = [
    path('create_firm/', CreateFirmFromURLView.as_view()),
    path('getfirms/', CreateFirmFromURLView.as_view()),
]
