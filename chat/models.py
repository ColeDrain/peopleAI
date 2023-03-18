from django.db import models
from django.contrib.auth.models import User


class Character(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(max_length=4000)
    about = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_input = models.TextField(verbose_name="User Input", null=True)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    character_response = models.TextField(verbose_name="Character Response", null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.character.name}"
