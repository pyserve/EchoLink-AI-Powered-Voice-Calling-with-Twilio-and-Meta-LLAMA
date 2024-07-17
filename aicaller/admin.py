from django.contrib import admin
from django.utils.html import format_html
from .models import *


class LeadAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name","email", "phone_number", "address", "call_lead"]

    def call_lead(self, obj):
        return format_html(
            '''<button class='btn btn-success' onclick="window.open('/call/lead/{}', '_blank');">
            <i class="fa fa-phone"></i> Call Lead</button>''',
            obj.pk
        )
    call_lead.short_description = 'Call Action'

admin.site.register(Lead, LeadAdmin)
admin.site.register(SalesAgent)
admin.site.register(Appointment)
admin.site.register(VoiceChat)
admin.site.register(VoiceMessage)
