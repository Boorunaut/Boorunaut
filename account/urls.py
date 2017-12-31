from django.conf.urls import url

from . import views

app_name = "account"

urlpatterns = [
    url(r'sign-in/$', views.sign_in, name='sign_in'),
]
