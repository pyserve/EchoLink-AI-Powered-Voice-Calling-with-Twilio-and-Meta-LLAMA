from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Lead, Appointment, SalesAgent, VoiceChat, VoiceMessage
from .serializers import UserSerializer, LeadSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse, Connect, Gather
from django.conf import settings
from huggingface_hub import InferenceClient

# using Facebook Meta-LLMA large language model for call reply.
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
client = InferenceClient(model=model_name, token=settings.HUGGINGFACE_TOKEN)

# Function to handle the incoming calls at the first time.
@csrf_exempt
def IncomingCallHandler(request):
    response = VoiceResponse()
    gather = Gather(input='speech', action=f'https://{settings.NGROK_URL}/inbounds-process/', timeout=3)
    gather.say('Welcome to Weaver Eco Home, please tell us why you\'re calling')
    response.append(gather)
    response.say("We didn't receive any input. Goodbye!")
    return HttpResponse(str(response), content_type='text/xml')

# Function to handle the call processing
@csrf_exempt
def IncomingCallProcessor(request):
    if request.method == "POST":
        prompt = ''
        if "prompt" not in request.session:
            request.session["prompt"] = []
        else:
            for message in request.session["prompt"]:
                if message["role"] == "user":
                    prompt += f"User: {message['content']}\n"
                elif message["role"] == "assistant":
                    prompt += f"Assitant: {message['content']}\n"

        response = VoiceResponse()
        if request.POST.get('SpeechResult', ""):
            speech = request.POST['SpeechResult']
            prompt += f"User: {speech}\n"
            request.session["prompt"].append({"role": "user", "content": speech})
            prompt += f"Assistant: "
            reply = ''
            for message in client.chat_completion(
                    messages=[{"role": "user", "content": speech}],
                    max_tokens=50,
                    stream=True,
                ):
                reply += message.choices[0].delta.content + ""
            gather = Gather(input='speech', action=f'https://{settings.NGROK_URL}/process/', timeout=3)
            response.append(gather)
            gather.say(reply)
            response.say("We didn't receive any input. Goodbye!")
            request.session["prompt"].append({"role": "assistant", "content": reply})
            request.session.modified = True
            return HttpResponse(str(response), content_type='text/xml')
        
    response.say("Sorry! something went wrong. We will contact you back soon.")
    return HttpResponse(str(response), content_type='text/xml')

@csrf_exempt
def OutgoingCallHandler(request, id=None):
    if id is not None:
        lead = Lead.objects.get(pk=id)
        lead = LeadSerializer(lead)
    return JsonResponse({"data": lead})

@csrf_exempt
def OutgoingCallProcessor(request, id=None):
    return JsonResponse({"data": ""})