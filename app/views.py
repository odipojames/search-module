from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import (RegisterSerializer,
        ApplicationSerializer, PaymentSerializer,
        CertificateSerializer, ReviewSerializer,
        UserSerializer,LoginSerializer,UserListSerializer)
from django.contrib.auth import get_user_model
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsApplicant, IsRegistrar, IsRegistrarInCharge
from django.shortcuts import get_object_or_404
from .models import OfficialSearchApplication



User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            })

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer        


class ApplicantApplicationCreateView(generics.CreateAPIView):
    queryset = OfficialSearchApplication.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsApplicant]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class ApplicantApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsApplicant]

    def get_queryset(self):
        return OfficialSearchApplication.objects.filter(applicant=self.request.user)


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsApplicant]

    def post(self, request, application_id):
        application = get_object_or_404(OfficialSearchApplication, id=application_id, applicant=request.user)
        if application.status != "pending":
            return Response({"error": "Payment already done or not allowed."}, status=400)

        serializer = PaymentSerializer(data=request.data, context={"application": application})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)  


class ApplicantDownloadCertificateView(generics.RetrieveAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsApplicant]

    def get_queryset(self):
        return Certificate.objects.filter(application__applicant=self.request.user)


class SubmittedApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsRegistrarInCharge]

    def get_queryset(self):
        return OfficialSearchApplication.objects.filter(
            status="submitted",
            registry=self.request.user.registry
        )

class AssignRegistrarView(APIView):
    permission_classes = [IsAuthenticated, IsRegistrarInCharge]

    def post(self, request, application_id):
        application = get_object_or_404(OfficialSearchApplication, id=application_id)

        # Optional: Ensure RIC can only assign applications from their own registry
        if request.user.registry != application.registry:
            return Response({"error": "You can only assign applications from your own registry."}, status=403)

        if application.status != "submitted":
            return Response({"error": "Only submitted applications can be assigned."}, status=400)

        serializer = AssignRegistrarSerializer(data=request.data, context={"application": application})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        registrar = serializer.validated_data["registrar_id"]

        return Response({
            "message": f"Application #{application.id} assigned to {registrar.username}"
        }, status=200)


class AssignedApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsRegistrar]

    def get_queryset(self):
        return OfficialSearchApplication.objects.filter(assigned_to=self.request.user)




class ApproveApplicationView(APIView):
    permission_classes = [IsAuthenticated, IsRegistrar]

    def post(self, request, application_id):
        app = get_object_or_404(OfficialSearchApplication, id=application_id, assigned_to=request.user)

        if app.status not in ["assigned"]:
            return Response({"error": "Cannot approve this application."}, status=400)

        serializer = CertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(application=app, uploaded_by=request.user)
        app.status = "completed"
        app.save()
        return Response({"message": "Application approved and certificate uploaded."})




class RejectApplicationView(APIView):
    permission_classes = [IsAuthenticated, IsRegistrar]

    def post(self, request, application_id):
        app = get_object_or_404(OfficialSearchApplication, id=application_id, assigned_to=request.user)

        if app.status not in ["assigned"]:
            return Response({"error": "Cannot reject this application."}, status=400)

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(application=app, reviewer=request.user)
        app.status = "rejected"
        app.save()
        return Response({"message": "Application rejected with review."})                




