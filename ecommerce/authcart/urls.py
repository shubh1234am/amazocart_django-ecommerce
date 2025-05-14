from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.handlelogin, name='handlelogin'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.handlelogout, name='handlelogout'),
    path('profile/', views.profile_view, name='profile'),
]
