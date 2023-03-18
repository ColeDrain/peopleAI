from django.contrib import admin
from .models import Character, Chat
# Register your models here.

class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'about')

class ChatAdmin(admin.ModelAdmin):
    list_display = ('character', 'user', 'user_input', 'character_response')

admin.site.register(Character, CharacterAdmin)
admin.site.register(Chat, ChatAdmin)
