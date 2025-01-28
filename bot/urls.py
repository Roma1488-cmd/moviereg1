from django.urls import path
from . import views

urlpatterns = [
    # Головна сторінка адмін панелі
    path('', views.dashboard, name='dashboard'),

    # Управління повідомленнями
    path('messages/', views.message_list, name='message_list'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),

    # Управління каналами
    path('channels/', views.channel_list, name='channel_list'),
    path('channels/add/', views.add_channel, name='add_channel'),
    path('channels/<int:channel_id>/edit/', views.edit_channel, name='edit_channel'),
    path('channels/<int:channel_id>/delete/', views.delete_channel, name='delete_channel'),

    # Управління користувачами
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/details/', views.user_details, name='user_details'),

    # Налаштування бота
    path('settings/', views.bot_settings, name='bot_settings'),
]
