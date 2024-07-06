from django.urls import path
from socialnetwork import views


urlpatterns = [
    path('', views.global_action, name='home'),
    path('login', views.login_action, name='login'),
    path('register', views.register_action, name='register'),
    path('logout', views.logout_action, name='logout'),
    path('global', views.global_action, name='global'),
    path('follower', views.follower_action, name='follower'),
    path('profile', views.user_profile_action, name='profile'),
    path('other-profile/<int:id>', views.follower_profile_action, name='other-profile'),
    path('photo/<int:id>', views.get_user_photo, name="photo"),
    path('get-global', views.get_global, name='get-global'),
    path('get-follower', views.get_follower, name='get-follower'),
    path('add-comment', views.add_comment, name='add-comment'),
]