from django.urls import path
from . views import *

urlpatterns = [
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name = 'logout'),
    path('register/', registerPage, name='register'),
    
    path('', home, name='home'),
    
    path('create_room', createRoom, name='create_room'),
    path('update_room/<int:pk>', updateRoom, name='update_room'),
    path('rooms/<int:pk>', room, name='room'),
    path('delete_room/<int:pk>', deleteRoom, name='delete_room'),
]
