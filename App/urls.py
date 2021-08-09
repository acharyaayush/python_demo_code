from django.conf.urls import url

from api import views
from api.views import *
from django.urls import path

urlpatterns = [
    path('checkversion', views.get_version),
    path('addversion', views.add_latest_version),
    path('auth', LoginView.as_view()),
    path('adminauth', AdminLoginView.as_view()),
    path('checksocial', SocialLoginView.as_view()),
    path('forgotpassword', ForgotPasswordView.as_view()),
    path('users', UserView.as_view()),
    path('searchuser', UserSearchAPI.as_view()),
    path('category', CategoryView.as_view()),
    path('searchcategory', CategorySearchAPI.as_view()),
    path('pushnotification', SendPushNotifications.as_view())
]