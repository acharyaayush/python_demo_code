from django.conf.urls import url

from api import views
from api.views import *
from django.urls import path

urlpatterns = [
    path('auth', views.LoginView.as_view()),
    path('adminauth', views.AdminLoginView.as_view()),
    path('checksocial', views.SocialLoginView.as_view()),
    path('forgotpassword', views.ForgotPasswordView.as_view()),
    path('users', views.UserView.as_view()),
    path('searchuser', views.UserSearchAPI.as_view()),
    path('pushnotification', views.SendPushNotifications.as_view())
]