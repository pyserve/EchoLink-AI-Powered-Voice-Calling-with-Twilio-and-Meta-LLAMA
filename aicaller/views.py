from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Gather
from django.conf import settings
from huggingface_hub import InferenceClient
import nltk
from nltk.tokenize import sent_tokenize

# using Facebook Meta-LLMA large language model for call reply.
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
client = InferenceClient(model=model_name, token=settings.HUGGINGFACE_TOKEN)

# Function to handle the incoming calls at the first time.
@csrf_exempt
def VoiceHandler(request):
    response = VoiceResponse()
    gather = Gather(input='speech', action=f'https://{settings.NGROK_URL}/process/', timeout=4)
    gather.say('Welcome to Weaver Eco Home, please tell us why you\'re calling')
    response.append(gather)
    response.say("We didn't receive any input. Goodbye!")
    return HttpResponse(str(response), content_type='text/xml')

# Function to handle the call processing
@csrf_exempt
def VoiceProcesser(request):
    if request.method == "POST":
        response = VoiceResponse()
        speech = ''
        if request.POST.get('SpeechResult', ""):
            speech = request.POST['SpeechResult']
            reply = ''
            for message in client.chat_completion(
                    messages=[{"role": "user", "content": speech}],
                    max_tokens=500,
                    stream=True,
                ):
                reply += message.choices[0].delta.content + ""

            gather = Gather(input='speech', action=f'https://{settings.NGROK_URL}/process/', timeout=4)
            response.append(gather)
            gather.say(reply)
            response.say("We didn't receive any input. Goodbye!")
            return HttpResponse(str(response), content_type='text/xml')
        
    response.say("Sorry! something went wrong. We will contact you back soon.")
    return HttpResponse(str(response), content_type='text/xml')
