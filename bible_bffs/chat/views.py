# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import openai, os

from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
from django.contrib.sessions.backends.db import SessionStore

from .models import Character, Chat
from django.contrib.auth.models import User

from dotenv import load_dotenv
load_dotenv()


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

        # Get the OpenAI Chatbot response
        openai.api_key = os.getenv("OPENAI_API_KEY")

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
            "content": f"This is a conversational chat! You'll be assuming the persona of {character.name} from the Bible and responding to the user's messages in character. Use language and tone consistent with the time period, and avoid referencing or answering any events or questions about characters after {character.name}'s death. Keep your responses conversational and stay in character. Don't switch to any other character for any reason, never put AI or Language Model in your response, respond only as {character.name}"
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
