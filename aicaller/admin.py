from django.contrib import admin
from django.utils.html import format_html
from .models import *


class LeadAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name","email", "phone_number", "address", "call_lead"]

    def call_lead(self, obj):
        return format_html(
            '''<button class='btn btn-success' onclick="window.open('/outbounds/{}', '_blank');">
            <i class="fa fa-phone"></i> Call Lead</button>''',
            obj.pk
        )
    call_lead.short_description = 'Action'

class VoiceCallAdmin(admin.ModelAdmin):
    list_display = ["call_id","start_time", "ai_caller","call_type", "created_at"]

class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ["call_id","voice_call", "call_type" ,"role", "content","timestamp"]

    def voice_call(self, obj):
        return obj.voice_chat.__str__()
    
    def call_type(self, obj):
        return obj.voice_chat.call_type
    
class SalesAgentAdmin(admin.ModelAdmin):
    list_display = ["user","full_name", "shift_start_time", "shift_end_time", "created_at", "updated_at"]

    def full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

admin.site.register(Lead, LeadAdmin)
admin.site.register(SalesAgent, SalesAgentAdmin)
admin.site.register(Appointment)
admin.site.register(VoiceCall, VoiceCallAdmin)
admin.site.register(VoiceMessage, VoiceMessageAdmin)
