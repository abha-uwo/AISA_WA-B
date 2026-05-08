from rest_framework import serializers
from .models import User, Client, Automation, Workflow

class ClientSerializer(serializers.ModelSerializer):
    _id = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = '__all__'

    def get__id(self, obj):
        return str(obj.id)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'role', 'status', 'client')
        extra_kwargs = {'password': {'write_only': True}}

class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = '__all__'
        read_only_fields = ('client',)

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ('client',)

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    businessName = serializers.CharField(required=False)

    def create(self, validated_data):
        email = validated_data['email'].lower().strip()
        business_name = validated_data.get('businessName', f"{validated_data['name']}'s Business")
        
        client = Client.objects.create(business_name=business_name)
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data['name'],
            role='CLIENT',
            status='PENDING',
            client=client
        )
        return user
