from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, ClientViewSet, AutomationViewSet, WorkflowViewSet, AdminStatsView, AdminAutomationsView, AdminMessagesView, WhatsAppWebhookView, AdminUsersView, ProfileView, ClientMessagesView, GlobalSettingsView, PlatformAssistantView

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'automations', AutomationViewSet, basename='automation')
router.register(r'workflows', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('messages/', ClientMessagesView.as_view(), name='client-messages'),
    path('admin/stats', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/automations', AdminAutomationsView.as_view(), name='admin-automations'),
    path('admin/messages', AdminMessagesView.as_view(), name='admin-messages'),
    path('admin/users', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>', AdminUsersView.as_view(), name='admin-user-detail'),
    path('platform-assistant/', PlatformAssistantView.as_view(), name='platform-assistant'),
    path('admin/settings/global', GlobalSettingsView.as_view(), name='global-settings'),
    path('webhook/whatsapp', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
]
