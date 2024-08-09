from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from .models import Lead, Appointment, SalesAgent, VoiceCall, VoiceMessage
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
# model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
client = InferenceClient(model=model_name, token=settings.HUGGINGFACE_TOKEN)

speaker_timeout = 5
twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_auth_token = settings.TWILIO_AUTH_TOKEN

@method_decorator(csrf_exempt, name='dispatch')
class InboundCalls(View):
    def __init__(self):
        self.welcome_message = "Welcome to Weaver Eco Home, please tell us why you\'re calling?"
        self.fallback_message = "We didn't receive any input. Thank you for Calling Weaver Eco Home. Have a good day and Goodbye!"
        self.closing_message = "Thank you for calling today! Enjoy your rest of the day."
        
    def get(self, request):
        phone_number = request.GET.get('From')
        leads = Lead.objects.filter(phone_number=phone_number)
        return render(request, "admin/aicaller/inbounds.html", {
            "data": request.GET,
            "callId": request.GET.get("CallSid"),
            "twilio_account_sid": twilio_account_sid,
            "twilio_auth_token": twilio_auth_token
        })

    def post(self, request):
        prompt = {
            "role": "system", 
            "content": f"""You are an AI voice call assistant at Weaver Eco Home for the role of
                customer support. Weaver Eco Home is an HVAC company that sells heat pump, 
                air conditioner, and so on. Please access the website for this company hosted at 
                https://www.weaverecohome.ca/ for more information. Please act the way to provide
                customer support asking them about problems. Only reply in two sentences.\n
            """
        }
        CallSid = request.POST.get("CallSid")
        call = VoiceCall.objects.filter(call_id=CallSid).first()
        if not call:
            call = VoiceCall(
                call_id = CallSid,
                ai_caller = "Beaver", 
                start_time = timezone.now(), 
                call_type = "inbound"
            )
            call.save()
            webbrowser.open_new(f"{settings.BASE_URL}/inbounds/?"+ urlencode(request.POST))
        
        response = VoiceResponse()
        if request.POST.get('SpeechResult', ""):
            speech = request.POST['SpeechResult']
            message = VoiceMessage.objects.create(
                voice_chat=call, role="user", content=speech, call_id=CallSid
            )
            messages = VoiceMessage.objects.filter(voice_chat = call)
            all_messages = [{"role": message.role, "content": message.content} for message in messages]
            reply = ''
            for message in client.chat_completion(
                    messages=[prompt, *all_messages, {"role": "user", "content": speech}],
                    max_tokens=120,
                    stream=True,
                ):
                reply += message.choices[0].delta.content + ""
            message = VoiceMessage.objects.create(
                voice_chat=call, role="assistant", content=reply, call_id=CallSid
            )
            gather = Gather(
                input='speech', 
                action=f'{settings.BASE_URL}/inbounds/', 
                timeout=speaker_timeout
            )
            response.append(gather)
            gather.say(reply)
            response.say(self.fallback_message)            
            return HttpResponse(str(response), content_type='text/xml')
        
        gather = Gather(
            input='speech', 
            action=f'{settings.BASE_URL}/inbounds/', 
            timeout=speaker_timeout,
        )
        gather.say(self.welcome_message)
        response.append(gather)
        response.say(self.fallback_message)
        return HttpResponse(str(response), content_type='text/xml')



@method_decorator(csrf_exempt, name='dispatch')
class OutboundsCalls(View):
    def __init__(self):
        self.fallback_message = "We didn't receive any input. Thank you for Calling Weaver Eco Home. Have a good day and Goodbye!"
        self.closing_message = "Thank you for calling today! Enjoy your rest of the day."

    def get(self, request, id=None):
        call_sid = None
        if id is not None:
            lead = Lead.objects.get(pk=id)
            client = Client(twilio_account_sid, twilio_auth_token)
            call = client.calls.create(
                from_=settings.TWILIO_PHONE_NUMBER,
                to=lead.phone_number,
                url=f'{settings.BASE_URL}/outbounds/{id}',
                method="POST",
            )
            call_sid = call.sid
            print(call_sid)
        return render(request, "admin/aicaller/outbounds.html", {
            "lead": lead, 
            "callId": call_sid, 
            "twilio_account_sid": twilio_account_sid, 
            "twilio_auth_token": twilio_auth_token
        })

    #prompt = Please ask about the size of their house, the type of gas they use, and the age of their furnace.
    def post(self, request, id=None):
        lead = Lead.objects.get(pk=id)
        system = {
            "role":"system",
            "content": f"""You are an AI voice call assistant at Weaver Eco Home, 
            making outbound calls for customer support. Weaver Eco Home is an HVAC company 
            that sells heat pumps, air conditioners, and more. You are calling {lead.first_name}, 
            a potential customer who inquired about heat pump.  Push the client to book an appointment for a 
            consultation based on available slots. Be conversational and cheerful. Keep responses short and up to two maximum sentences.\n"""
        }
        prompt = {
            "role": "assistant",
            "content": f"""
                Hi! Am I speaking to {lead.first_name}? 
            """
        }
        CallSid = request.POST.get("CallSid")
        call = VoiceCall.objects.filter(call_id=CallSid).first()
        if not call:
            chat = VoiceCall(
                lead = lead,
                call_id=request.POST.get("CallSid"),
                ai_caller="Beaver", 
                start_time=timezone.now(), 
                call_type='outbound'
            )
            chat.save()

        response = VoiceResponse()
        if request.POST.get('SpeechResult', ""):
            speech = request.POST['SpeechResult']
            message = VoiceMessage.objects.create(
                voice_chat=call, role="user", content=speech, call_id=CallSid
            )
            messages = VoiceMessage.objects.filter(voice_chat = call)
            all_messages = [{"role": message.role, "content": message.content} for message in messages]
            reply = ''
            for message in client.chat_completion(
                    messages=[system, prompt, *all_messages, {"role": "user", "content": speech}],
                    max_tokens=50,
                    stream=True,
                ):
                reply += message.choices[0].delta.content + ""
            message = VoiceMessage.objects.create(
                voice_chat=call, role="assistant", content=reply, call_id=CallSid
            )
            gather = Gather(
                input='speech', 
                action=f'{settings.BASE_URL}/outbounds/{id}', 
                timeout=speaker_timeout
            )
            response.append(gather)
            gather.say(reply)
            response.say(self.fallback_message)
            self.intent_recognition(context= all_messages)
            return HttpResponse(str(response), content_type='text/xml')
            
        gather = Gather(
            input='speech', 
            action=f'{settings.BASE_URL}/outbounds/{id}', 
            timeout=speaker_timeout
        )
        response.append(gather)
        gather.say(prompt['content'])
        response.say(self.fallback_message)
        return HttpResponse(str(response), content_type='text/xml')

    def intent_recognition(self, context):
        current_date = timezone.now()

        prompt = f"""
            Analyze the entire conversation between the assistant and the
            user to identify any booking intent. 
            Determine the appointment time relative to the current date which is {current_date}.
            Provide the results in the following only JSON formatted string, nothing else:

            "intent": "booking",
            "appointment_time": "YYYY-MM-DDTHH:MM:SSZ"

            Make sure the `appointment_time` is accurate and based on the user's intent and context from the conversation.
            context = {context}
            """
        
        reply = ''
        for message in client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                stream=True, 
                # The model sends partial responses as they are generated, 
                # rather than waiting to send the entire response at once.
            ):
            reply += message.choices[0].delta.content or ""
        print((reply))