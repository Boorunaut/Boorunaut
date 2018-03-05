from django.conf.urls import url
from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
]
