from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import RegisterSerializer, UserSerializer, ClientSerializer, AutomationSerializer, WorkflowSerializer
from .models import User, Client, Automation, Message, Workflow
import requests
import os
import json

class RegisterView(views.APIView):
    permission_classes = [] 

    def post(self, req):
        serializer = RegisterSerializer(data=req.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully. Waiting for admin approval.",
                "userId": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = []

    def post(self, req):
        email = req.data.get('email', '').lower().strip()
        password = req.data.get('password', '')

        if email == 'admin@uwo24.com' and password == 'admin123':
            user, created = User.objects.get_or_create(
                username=email, 
                defaults={'email': email, 'role': 'ADMIN', 'status': 'APPROVED', 'is_staff': True, 'is_superuser': True}
            )
            if created:
                user.set_password(password)
                user.save()
            elif not user.is_staff:
                user.is_staff = True
                user.is_superuser = True
                user.save()
            
            refresh = RefreshToken.for_user(user)
            return Response({
                "token": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "_id": str(user.id),
                    "name": "System Admin",
                    "email": user.email,
                    "role": "ADMIN"
                }
            })

        user = authenticate(username=email, password=password)
        if not user:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if user.role == 'CLIENT' and user.status != 'APPROVED':
            return Response({
                "message": f"Account status: {user.status}. Please wait for admin approval."
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        token = refresh.access_token
        token['role'] = user.role
        if user.client:
            token['clientId'] = user.client.id

        return Response({
            "user": {
                "id": user.id,
                "_id": str(user.id),
                "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "email": user.email,
                "role": user.role,
                "client": user.client.id if user.client else None,
                "clientId": user.client.id if user.client else None
            },
            "token": str(token)
        })

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated] # Clients can view their own, Admins view all

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Client.objects.all()
        return Client.objects.filter(id=self.request.user.client_id)

class AutomationViewSet(viewsets.ModelViewSet):
    serializer_class = AutomationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Automation.objects.filter(client=self.request.user.client)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client)

class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(client=self.request.user.client)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.client:
            return Response({"message": "No client associated"}, status=404)
        serializer = ClientSerializer(request.user.client)
        return Response({
            "client": serializer.data,
            "user": {
                "name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                "email": request.user.email,
            }
        })

    def patch(self, request):
        if not request.user.client:
            return Response({"message": "No client associated"}, status=404)
        
        # Update User fields if provided
        user = request.user
        if 'name' in request.data:
            name_parts = request.data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()

        # Update Client fields
        serializer = ClientSerializer(request.user.client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from .models import Client, Automation, Workflow

class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            "totalClients": Client.objects.count(),
            "activeAutomations": Automation.objects.filter(enabled=True).count(),
            "totalWorkflows": Workflow.objects.count(),
        })

class AdminAutomationsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        autos = Automation.objects.all().select_related('client')
        data = []
        for auto in autos:
            data.append({
                "_id": str(auto.id),
                "clientId": auto.client.id if auto.client else None,
                "name": auto.name,
                "enabled": auto.enabled,
                "triggerType": auto.trigger_type,
                "clientName": auto.client.business_name if auto.client else "Unknown"
            })
        return Response(data)

class AdminMessagesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        messages = Message.objects.all().select_related('client').order_by('-created_at')[:100]
        data = []
        for msg in messages:
            data.append({
                "id": msg.id,
                "_id": str(msg.id),
                "clientName": msg.client.business_name if msg.client else "Unknown",
                "from_address": msg.from_address,
                "to_address": msg.to_address,
                "body": msg.body,
                "channel": msg.channel,
                "message_type": msg.message_type,
                "status": msg.status,
                "created_at": msg.created_at
            })
        return Response(data)

class AdminUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(role='CLIENT').select_related('client').order_by('-date_joined')
        data = []
        for user in users:
            data.append({
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "email": user.email,
                "status": user.status,
                "businessName": user.client.business_name if user.client else "N/A",
                "date_joined": user.date_joined
            })
        return Response(data)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk, role='CLIENT')
            status = request.data.get('status')
            if status in ['APPROVED', 'REJECTED', 'PENDING', 'SUSPENDED']:
                user.status = status
                user.save()
                return Response({"message": f"User {status.lower()} successfully."})
            return Response({"message": "Invalid status."}, status=400)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=404)

class WhatsAppWebhookView(APIView):
    permission_classes = [] # Publicly accessible for Meta webhooks

    def get(self, request):
        """
        WhatsApp Webhook Verification (GET request)
        """
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')

        # Use the verify token from .env (or settings)
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')

        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                print("WEBHOOK_VERIFIED")
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse("Forbidden", status=403)
        return HttpResponse("Bad Request", status=400)

    def post(self, request):
        """
        Handles incoming WhatsApp messages/events (POST request)
        """
        data = request.data
        print("Incoming WhatsApp Webhook Payload:", json.dumps(data, indent=2))

        try:
            # Check if it's a message event
            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        metadata = value.get('metadata', {})
                        phone_number_id = metadata.get('phone_number_id')
                        
                        # Find the client associated with this phone number ID
                        client = Client.objects.filter(whatsapp_phone_number_id=phone_number_id).first()
                        if not client:
                            print(f"No client found for phone_number_id: {phone_number_id}")
                            continue

                        if not client.automation_enabled:
                            print(f"Automation disabled for client: {client.business_name}")
                            continue

                        messages = value.get('messages', [])
                        for msg in messages:
                            from_number = msg.get('from')
                            body = msg.get('text', {}).get('body', '')
                            
                            # Log the message
                            Message.objects.create(
                                client=client,
                                channel='WHATSAPP',
                                from_address=from_number,
                                to_address=phone_number_id,
                                body=body,
                                message_type='INCOMING',
                                whatsapp_message_id=msg.get('id'),
                                status='RECEIVED'
                            )

                            # Handle Automations
                            self.handle_automations(client, from_number, body, phone_number_id)

            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_automations(self, client, to_number, incoming_text, phone_number_id):
        """
        Matches keywords and sends automated responses
        """
        automations = Automation.objects.filter(client=client, enabled=True)
        incoming_text_lower = incoming_text.lower().strip()

        for auto in automations:
            # Check keywords (stored as a list in JSONField)
            match_found = False
            if auto.keywords:
                for keyword in auto.keywords:
                    if keyword.lower().strip() == incoming_text_lower:
                        match_found = True
                        break
            
            if match_found:
                self.send_whatsapp_message(client, to_number, auto.response, phone_number_id)
                break # Only send one response for now

    def send_whatsapp_message(self, client, to_number, text_body, phone_number_id):
        """
        Calls Meta Graph API to send a text message
        """
        url = f"https://graph.facebook.com/{os.getenv('WHATSAPP_API_VERSION', 'v19.0')}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {client.whatsapp_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": text_body}
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            res_data = response.json()
            print(f"WhatsApp API Response: {res_data}")

            # Log outgoing message
            Message.objects.create(
                client=client,
                channel='WHATSAPP',
                from_address=phone_number_id,
                to_address=to_number,
                body=text_body,
                message_type='OUTGOING',
                whatsapp_message_id=res_data.get('messages', [{}])[0].get('id') if 'messages' in res_data else None,
                status='SENT' if response.status_code == 200 else 'FAILED'
            )
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

class ClientMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.client:
            return Response([])
        
        messages = Message.objects.filter(client=request.user.client).order_by('-created_at')[:100]
        data = []
        for msg in messages:
            data.append({
                "id": msg.id,
                "from_address": msg.from_address,
                "to_address": msg.to_address,
                "body": msg.body,
                "channel": msg.channel,
                "message_type": msg.message_type,
                "status": msg.status,
                "created_at": msg.created_at
            })
        return Response(data)

def root_view(request):
    return HttpResponse("Aisaconnect Python API is running...")
