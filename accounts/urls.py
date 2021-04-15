from django.urls import path

from .views import SignUpView, view_user_profile

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', view_user_profile, name='profile'),
]
