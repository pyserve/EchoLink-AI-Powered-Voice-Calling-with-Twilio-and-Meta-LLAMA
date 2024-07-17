from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

LEAD_SOURCE_CHOICES = [
    ('weaverecohome', 'Weaverecohome.ca'),
    ('bought_lead', 'Bought Lead'),
    ('morocco', 'Morocco'),
    ('c_social_ext', 'C Social (EXT)'),
    ('c_social_int', 'C Social (INT)'),
    ('call_center_weh_d', 'Call Center - WEH - D'),
    ('current_customer', 'Current Customer'),
    ('dealer', 'Dealer'),
    ('door_to_door', 'Door to Door'),
    ('email', 'Email'),
    ('facebook_cmc', 'Facebook (CMC)'),
    ('facebook_da', 'Facebook (DA)'),
    ('facebook_vu', 'Facebook (VU)'),
    ('follow_up_appointment', 'Follow Up Appointment'),
    ('google', 'Google'),
    ('instagram', 'Instagram'),
    ('promo', 'Promo'),
    ('referral', 'Referral'),
    ('sms', 'SMS'),
    ('website', 'Website'),
    ('youtube', 'Youtube'),
    ('other', 'Other'),
    ('online_da', 'Online (DA)')
]

SERVICE_CHOICES = [
    ('attic', 'Attic'),
    ('hvac_check_up', 'HVAC Check Up'),
    ('hybrid_heating_system', 'Hybrid Heating System'),
    ('heat_pump', 'Heat Pump'),
    ('gas_bill_savings', 'Gas Bill Savings'),
    ('electricity_bill_savings', 'Electricity Bill Savings'),
    ('free_ac', 'Free AC'),
]

class SalesAgent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"
    
class Lead(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    interested = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    lead_source = models.CharField(max_length=100, choices=LEAD_SOURCE_CHOICES)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Appointment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='appointments')
    agent = models.ForeignKey(SalesAgent, on_delete=models.CASCADE, related_name='agents')
    appointment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lead} - Appointment on {self.appointment_date}"
    
class VoiceChat(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='voice_chats')
    ai_caller = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    CALL_TYPES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    call_type = models.CharField(max_length=50, choices=CALL_TYPES)
    duration_seconds = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VoiceChat {self.id} ({self.lead} with {self.ai_caller})"

    class Meta:
        ordering = ['-start_time']

class VoiceMessage(models.Model):
    voice_chat = models.ForeignKey(VoiceChat, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # 'user' or 'assistant'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content} ({self.timestamp})"