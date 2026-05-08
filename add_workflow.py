import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
from api.models import Client, Workflow

client = Client.objects.get(id=1)

nodes = [
    { "id": "1", "type": "TRIGGER", "label": "Customer greets", "content": "Hi, Welcome to KB Bank.", "x": 100, "y": 100 },
    { "id": "2", "type": "BUTTONS", "label": "Main Menu", "buttons": ["Check Balance", "Mini Statement"], "x": 100, "y": 400 },
    { "id": "3", "type": "MESSAGE", "label": "Final Response", "content": "Your balance is ₹1,24,500.23", "x": 500, "y": 400 }
]

connections = [
    { "from": "1", "to": "2" },
    { "from": "2", "to": "3" }
]

Workflow.objects.create(
    client=client,
    name="Banking Support Bot",
    trigger_type="KEYWORD",
    trigger_value=[],
    steps={"nodes": nodes, "connections": connections},
    enabled=True
)

print("Workflow added successfully!")
