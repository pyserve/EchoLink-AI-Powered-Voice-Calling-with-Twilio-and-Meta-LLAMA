from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from .models import Lead, Appointment, SalesAgent, VoiceChat, VoiceMessage
from .serializers import UserSerializer, LeadSerializer
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from huggingface_hub import InferenceClient
import webbrowser
from urllib.parse import urlencode
from django.utils import timezone

# using Facebook Meta-LLMA large language model for call reply.
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
client = InferenceClient(model=model_name, token=settings.HUGGINGFACE_TOKEN)

speaker_timeout = 3
twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_auth_token = settings.TWILIO_AUTH_TOKEN

@method_decorator(csrf_exempt, name='dispatch')
class InboundCalls(View):
    def get(self, request):
        phone_number = request.GET.get('From')
        leads = Lead.objects.filter(phone_number=phone_number)
        print(leads)
        return render(request, "admin/aicaller/inbounds.html", {
            "data": request.GET,
            "callId": request.GET.get("CallSid"),
            "twilio_account_sid": twilio_account_sid,
            "twilio_auth_token": twilio_auth_token
        })

    def post(self, request):
        prompt = ''
        if "call_id" not in request.session:
            request.session['call_id'] = request.POST.get("CallSid")
            webbrowser.open_new(f"{settings.BASE_URL}/inbounds/?"+ urlencode(request.POST))
            chat = VoiceChat(
                call_id=request.POST.get("CallSid"),
                ai_caller="Beaver", 
                start_time=timezone.now(), 
                call_type='inbound'
            )
            chat.save()
        else:
            chat = VoiceChat.objects.get(
                call_id=request.session['call_id']
            )
            print(chat)
        
        if "prompts" not in request.session:
            request.session["prompts"] = []
        else:
            for message in request.session["prompts"]:
                if message["role"] == "user":
                    prompt += f"User: {message['content']}\n"
                elif message["role"] == "assistant":
                    prompt += f"Assitant: {message['content']}\n"

        response = VoiceResponse()
        if request.POST.get('SpeechResult', ""):
            speech = request.POST['SpeechResult']
            message = VoiceMessage(voice_chat=chat, role="user", content=speech, call_id=request.POST.get("CallSid"))
            message.save()
            prompt += f"User: {speech}\n"
            request.session["prompts"].append({"role": "user", "content": speech})
            prompt += f"Assistant: "
            reply = ''
            for message in client.chat_completion(
                    messages=[{"role": "user", "content": speech}],
                    max_tokens=60,
                    stream=True,
                ):
                reply += message.choices[0].delta.content + ""
            message = VoiceMessage(voice_chat=chat, role="assistant", content=reply, call_id=request.POST.get("CallSid"))
            message.save()
            gather = Gather(input='speech', action=f'{settings.BASE_URL}/inbounds/', timeout=speaker_timeout)
            response.append(gather)
            gather.say(reply)
            response.say("We didn't receive any input. Goodbye!")
            request.session["prompts"].append({"role": "assistant", "content": reply})
            request.session.modified = True
            return HttpResponse(str(response), content_type='text/xml')
        
        response = VoiceResponse()
        gather = Gather(input='speech', action=f'{settings.BASE_URL}/inbounds/', timeout=speaker_timeout, \
            partial_result_callback=f"{settings.BASE_URL}/inbounds/", partial_result_callback_method="GET")
        gather.say('Welcome to Weaver Eco Home, please tell us why you\'re calling')
        response.append(gather)
        response.say("We didn't receive any input. Goodbye!")
        return HttpResponse(str(response), content_type='text/xml')


@method_decorator(csrf_exempt, name='dispatch')
class OutboundsCalls(View):
    def get(self, request, id=None):
        call_sid = None
        if id is not None:
            lead = Lead.objects.get(pk=id)
            phone = lead.phone_number
            client = Client(twilio_account_sid, twilio_auth_token)
            call = client.calls.create(
                method="POST",
                url=f'{settings.BASE_URL}/outbounds/{id}',
                # status_callback="https://127.0.0.1:8000/callback",
                # status_callback_method="POST",
                to=phone,
                from_=settings.TWILIO_PHONE_NUMBER,
            )
            call_sid = call.sid
            print(call_sid)
            self.lead = lead
        return render(request, "admin/aicaller/outbounds.html", {
            'lead': lead, 
            "callId": call_sid, 
            "twilio_account_sid": twilio_account_sid, 
            "twilio_auth_token": twilio_auth_token
        })

    def post(self, request, id=None):
        lead = Lead.objects.get(pk=id)
        initialPrompt = f'Hi! {lead.first_name}, I am calling you from Weaver Eco Home. I see you you are interested in {lead.interested}.'
        prompt = ''

        if "call_id" not in request.session:
            request.session['call_id'] = request.POST.get("CallSid")
            chat = VoiceChat(
                lead = lead,
                call_id=request.POST.get("CallSid"),
                ai_caller="Beaver", 
                start_time=timezone.now(), 
                call_type='outbound'
            )
            chat.save()
        else:
            chat = VoiceChat.objects.get(
                call_id=request.session['call_id']
            )
            print(chat)

        if "prompts" not in request.session:
            request.session["prompts"] = [{"role": "user", "content": initialPrompt}]
        else:
            for message in request.session["prompts"]:
                if message["role"] == "user":
                    prompt += f"User: {message['content']}\n"
                elif message["role"] == "assistant":
                    prompt += f"Assitant: {message['content']}\n"

        response = VoiceResponse()

        if request.POST.get('SpeechResult', ""):
            speech = request.POST['SpeechResult']
            message = VoiceMessage(voice_chat=chat, role="user", content=speech, call_id=request.POST.get("CallSid"))
            message.save()
            prompt += f"User: {speech}\n"
            request.session["prompts"].append({"role": "user", "content": speech})
            prompt += f"Assistant: "
            reply = ''
            for message in client.chat_completion(
                    messages=[{"role": "user", "content": speech}],
                    max_tokens=50,
                    stream=True,
                ):
                reply += message.choices[0].delta.content + ""
            message = VoiceMessage(voice_chat=chat, role="assistant", content=reply, call_id=request.POST.get("CallSid"))
            message.save()
            gather = Gather(input='speech', action=f'{settings.BASE_URL}/outbounds/{id}', timeout=speaker_timeout)
            response.append(gather)
            gather.say(reply)
            response.say("We didn't receive any input. Goodbye!")
            request.session["prompts"].append({"role": "assistant", "content": reply})
            request.session.modified = True
            return HttpResponse(str(response), content_type='text/xml')
            
        gather = Gather(input='speech', action=f'{settings.BASE_URL}/outbounds/{id}', timeout=speaker_timeout)
        response.append(gather)
        gather.say(prompt)
        response.say("We didn't receive any input. Goodbye!")
        request.session.modified = True
        return HttpResponse(str(response), content_type='text/xml')