from django.contrib import admin
from .models import *


class LeadAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name","email", "phone_number", "address"]

admin.site.register(Lead, LeadAdmin)
admin.site.register(SalesAgent)
admin.site.register(Appointment)
admin.site.register(VoiceChat)
admin.site.register(VoiceMessage)
