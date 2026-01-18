"""
URLs for accounts app.
"""
from django.urls import path
from .views import SignUpView, sign_in_view, current_user_view

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', sign_in_view, name='login'),
    path('me/', current_user_view, name='current_user'),
]
