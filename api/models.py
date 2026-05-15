from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    business_name = models.CharField(max_length=255)
    automation_enabled = models.BooleanField(default=True)
    
    # Enablement Flags
    facebook_enabled = models.BooleanField(default=False)
    instagram_enabled = models.BooleanField(default=False)
    
    # WhatsApp Config
    whatsapp_access_token = models.TextField(null=True, blank=True)
    whatsapp_phone_number_id = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_waba_id = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_verify_token = models.CharField(max_length=100, null=True, blank=True)
    
    # Global Greeting Message
    greeting_enabled = models.BooleanField(default=False)
    greeting_message = models.TextField(null=True, blank=True)
    greeting_buttons = models.JSONField(default=list, blank=True)
    
    # AI Assistant Config
    ai_enabled = models.BooleanField(default=False)
    ai_context = models.TextField(null=True, blank=True) # Description of business/platform for the AI
    
    # Config as JSON
    facebook_config = models.JSONField(default=dict, blank=True)
    instagram_config = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Automation(models.Model):
    TRIGGER_CHOICES = [
        ('KEYWORD', 'Keyword'),
        ('START_CHAT', 'Start Chat'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='automations')
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='KEYWORD')
    keywords = models.JSONField(default=list, blank=True)
    response = models.TextField()
    buttons = models.JSONField(default=list, blank=True) # Optional buttons (max 3)
    channels = models.JSONField(default=list, blank=True)  # e.g., ["WHATSAPP"]
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Workflow(models.Model):
    TRIGGER_CHOICES = [
        ('KEYWORD', 'Keyword'),
        ('NEW_CHAT', 'New Chat'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='KEYWORD')
    trigger_value = models.JSONField(default=list, blank=True)
    steps = models.JSONField(default=list)  # List of step dicts
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    CHANNEL_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram'),
    ]
    TYPE_CHOICES = [
        ('INCOMING', 'Incoming'),
        ('OUTGOING', 'Outgoing'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('RECEIVED', 'Received'),
        ('FAILED', 'Failed'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='messages')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    body = models.TextField()
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    whatsapp_message_id = models.CharField(max_length=255, null=True, blank=True)
    meta_message_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Log(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    action = models.CharField(max_length=255)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class GlobalSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    file = models.FileField(upload_to='legal/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key
