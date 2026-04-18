from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.home,            name='home'),
    path('register/',             views.register_view,   name='register'),
    path('login/',                views.login_view,      name='login'),
    path('logout/',               views.logout_view,     name='logout'),
    path('dashboard/',            views.dashboard,       name='dashboard'),
    path('upload/',               views.upload_artifact, name='upload_artifact'),
    path('review/',               views.review_queue,    name='review_queue'),
    path('vote/',                 views.vote,            name='vote'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('setup-admin/', views.create_super, name='create_super'),
]