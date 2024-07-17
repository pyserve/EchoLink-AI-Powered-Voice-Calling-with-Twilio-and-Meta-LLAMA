from django.core.serializers import serialize
import json


def UserSerializer(user):
    fields = '__all__'
    serialized_user = serialize("json", [user, ],)
    return json.loads(serialized_user)[0]
    
def LeadSerializer(lead):
    fields = '__all__'
    serialized_lead = serialize("json", [lead, ],)
    return json.loads(serialized_lead)[0]