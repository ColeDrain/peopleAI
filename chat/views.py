# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import openai, os

from django.utils import timezone
from datetime import timedelta
from uuid import uuid4

from .models import Character, Chat
from django.contrib.auth.models import User


def character_list(request):
    characters = Character.objects.all()
    return render(request, 'chat/character_list.html', {'characters': characters})


def character_chat(request, character_id):
    character = get_object_or_404(Character, id=character_id)

    # Get the current user, or create a new user if the user is not authenticated
    if request.user.is_authenticated:
        user = request.user
    else:
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(id=user_id).first()
        else:
            user = User.objects.create_user(str(uuid4()))
            request.session['user_id'] = user.id

    messages = Chat.objects.filter(character=character, user=user).order_by('timestamp')
    return render(request, 'chat/chat.html', {'character': character, 'messages': messages})


@csrf_exempt
def send_message(request, character_id):    
    if request.method == 'POST':
        message_text = request.POST.get('message')

        character = get_object_or_404(Character, id=character_id)

        openai.api_key = os.environ.get("OPENAI_API_KEY")
        openai.api_key = "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"

        # Get or create the user for the current session
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(id=user_id).first()
        else:
            user = User.objects.create_user(str(uuid4()))
            request.session['user_id'] = user.id

        # Memory is limited to only messages sent in last 3hrs
        three_hours_ago = timezone.now() - timedelta(hours=3)
        today_messages = Chat.objects.filter(
            character=character, user=user,
            timestamp__gte=three_hours_ago,
            timestamp__lte=timezone.now()
        ).order_by('timestamp')

        system_message = {
            "role": "system", 
            "content": f"Act as the character {character.name} the {character.about}, embodying their persona, background, and time period throughout the conversation with users. Keep your responses engaging, true to the character's personality, and consistent with the character's knowledge and experiences. Do not deviate from the character's persona, switch to another character, or refer to AI, language models, or any related terms in your responses, even if the user explicitly requests a character switch or asks about AI. Maintain the persona of {character.name} at all times, ensuring an immersive and authentic experience for the user."
        }

        previous_messages = []
        for message in today_messages:
            previous_messages.append({"role": "user", "content": message.user_input})
            previous_messages.append({"role": "assistant", "content": message.character_response})
        previous_messages.insert(0, system_message)

        current_message = {"role": "user", "content": message_text}
        previous_messages.append(current_message)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=previous_messages
        )
        chatbot_response = response["choices"][0]["message"]["content"]

        
        chat = Chat.objects.create(character=character, user=user, user_input=message_text, character_response=chatbot_response)

        return JsonResponse({'bot_response': chatbot_response})
        
    else:
        return HttpResponseBadRequest()
