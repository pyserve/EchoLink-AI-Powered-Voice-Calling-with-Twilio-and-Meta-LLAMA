import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from twilio.twiml.voice_response import VoiceResponse
import json
import base64
import wave
from pydub import AudioSegment
import io
from aicaller.settings import BASE_DIR

logger = logging.getLogger(__name__)

class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.payloads = []
        self.tracks = None
        self.mediaFormat = None
        logger.info("WebSocket connection established")
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"WebSocket connection closed: {close_code}")
        pass
    
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data['event'] == "start":
            self.tracks = data['start']['tracks']
            self.mediaFormat = data['start']['mediaFormat']

        if data['event'] == "media":
            self.payloads.append(data['media']['payload'])
        
        if data['event'] == "stop":
            decoded_data = bytearray(base64.b64decode(''.join(self.payloads)))
            
            # Convert μ-law to PCM using pydub
            audio_segment = AudioSegment(
                data=bytes(decoded_data),
                sample_width=1,  # μ-law is 8-bit
                frame_rate=self.mediaFormat['sampleRate'],
                channels=self.mediaFormat['channels']
            )
            pcm_audio = audio_segment.set_sample_width(2)  # Convert to 16-bit PCM

            # Save the PCM audio to a temporary file with dynamic name
            output_file = f"output_audio_file.wav"
            pcm_audio.export(output_file, format="wav")

            print(f'{output_file} generated.')

        response = await self.process_audio_data(bytes_data)
        await self.send(text_data=response)

    async def process_audio_data(self, audio_data):
        response = VoiceResponse()
        response.say("Hello. I am Joanna and I speak American English!")
        return str(response)

'''
{ 
 "event": "media",
 "sequenceNumber": "4",
 "media": { 
   "track": "inbound", 
   "chunk": "2", 
   "timestamp": "5",
   "payload": "no+JhoaJjpzS..."
 },
"streamSid": "MZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" 
}
'''

'''
{
'event': 'stop', 
'sequenceNumber': '160', 
'streamSid': 'MZ622bcc45a42b7bb125e840810de03621', 
'stop': {'accountSid': 'ACcc79daa381cd2eaa490fee6ca817c50d', 
'callSid': 'CAe0ffe403a411fff951555e55ea31daa9'
}
'''

# {'event': 'connected', 'protocol': 'Call', 'version': '1.0.0'}

'''
{
  "event": "start",
  "sequenceNumber": "1",
  "start": {
    "accountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "streamSid": "MZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "callSid": "CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "tracks": [ "inbound" ],
    "mediaFormat": { 
        "encoding": "audio/x-mulaw", 
        "sampleRate": 8000, 
        "channels": 1 },
    "customParameters": {
     "FirstName": "Jane",
     "LastName": "Doe",
     "RemoteParty": "Bob", 
   },
  },
  "streamSid": "MZXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
'''