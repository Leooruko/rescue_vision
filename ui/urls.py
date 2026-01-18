"""
URLs for UI app.
"""
from django.urls import path
from .views import (
    index_view,
    dashboard_view,
    case_detail_view,
    notifications_view,
    sign_up_view,
    sign_in_view,
    logout_view
)

app_name = 'ui'

urlpatterns = [
    path('', index_view, name='index'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('case/<uuid:case_id>/', case_detail_view, name='case_detail'),
    path('notifications/', notifications_view, name='notifications'),
    path('signup/', sign_up_view, name='signup'),
    path('signin/', sign_in_view, name='signin'),
    path('logout/', logout_view, name='logout'),
]
