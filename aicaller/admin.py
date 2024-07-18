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

class VoiceChatAdmin(admin.ModelAdmin):
    list_display = ["call_id","start_time", "ai_caller","call_type", "created_at"]

class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ["call_id","role", "content","timestamp"]

admin.site.register(Lead, LeadAdmin)
admin.site.register(SalesAgent)
admin.site.register(Appointment)
admin.site.register(VoiceChat, VoiceChatAdmin)
admin.site.register(VoiceMessage, VoiceMessageAdmin)
