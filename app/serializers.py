from rest_framework import serializers
from .models import (
    OfficialSearchApplication,
    Payment,
    Certificate,
    Review
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "county", "registry", "role"]  

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "county", "registry", "role"] 

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            county=validated_data["county"],
            registry=validated_data.get("registry"),  
            role=validated_data.get("role", "normal"),
        )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'county', 'registry']



class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficialSearchApplication
        fields = "__all__"
        read_only_fields = ["applicant", "status", "assigned_to", "submitted_at"]


class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=1050)
    application = serializers.PrimaryKeyRelatedField(read_only=True)  
    invoice_number = serializers.CharField(read_only=True)         
    payment_reference = serializers.CharField(read_only=True) 
    class Meta:
        model = Payment
        exclude = ['invoice_number', 'payment_reference']

    def validate_amount(self, value):
        if value != 1050:
            raise serializers.ValidationError("Amount must be exactly Ksh 1050")
        return value

    def create(self, validated_data):
        application = self.context["application"]
        validated_data["application"] = application
        validated_data["amount"] = 1050  # hardcode amount for safety
        payment = super().create(validated_data)

        # Update application status
        application.status = "submitted"
        application.save()

        return payment

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"
        read_only_fields = ["application", "uploaded_by", "uploaded_at"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["application", "reviewer", "created_at"]



class AssignRegistrarSerializer(serializers.Serializer):
    registrar_id = serializers.IntegerField()

    def validate_registrar_id(self, value):
        application = self.context.get("application")
        if not application:
            raise serializers.ValidationError("Missing application context.")

        try:
            # Registrar must have correct role and same registry as the application
            registrar = User.objects.get(
                id=value,
                role="is_registrar",
                registry=application.registry
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Registrar not found or not in the application's registry.")

        return registrar

    def save(self, **kwargs):
        application = self.context["application"]
        registrar = self.validated_data["registrar_id"]

        application.assigned_to = registrar
        application.status = "assigned"
        application.save()
        return application
