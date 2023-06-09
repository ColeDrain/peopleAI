from django.urls import path

from .views import character_list, character_chat, send_message

urlpatterns = [
    path('', character_list, name='character_list'),
    path('chat/<int:character_id>/', character_chat, name='character_chat'),
    path('<int:character_id>/send-message/', send_message, name='send_message'),
]
