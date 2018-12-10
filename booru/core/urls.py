from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path('terms_of_service/', views.TermsOfServiceView.as_view(), name="terms_of_service"),
    path('privacy_policy/', views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path('staff_page/hash_ban/', views.BannedHashCreateView.as_view(), name="hash_ban"),
    path('staff_page/hash_ban/<int:pk>/delete', views.BannedHashDeleteView.as_view(), name="hash_ban_delete"),
    path('staff_page/mod_queue/', views.ModQueueView.as_view(), name="mod_queue"),
    path('staff_page/mod_queue/<int:pk>/resolve', views.StaffPostFlagResolveView.as_view(), name="mod_queue_resolve"),
]
