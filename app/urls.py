from django.urls import path
from .views import (RegisterView, LoginView,
                    ApplicantApplicationCreateView, ApplicantApplicationListView,
    PaymentCreateView, ApplicantDownloadCertificateView,
    SubmittedApplicationsListView, AssignRegistrarView,
    AssignedApplicationsListView, ApproveApplicationView,
    RejectApplicationView,UserListView)

urlpatterns = [
    #authentication
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("users", UserListView.as_view(), name="user-list"),

     # Applicant
    path("applications/create", ApplicantApplicationCreateView.as_view()),
    path("applications", ApplicantApplicationListView.as_view()),
    path("applications/<int:application_id>/pay", PaymentCreateView.as_view()),
    path("certificates/<int:pk>", ApplicantDownloadCertificateView.as_view()),

    # Registrar In Charge
    path("registrar-in-charge/submitted", SubmittedApplicationsListView.as_view()),
    path("registrar-in-charge/assign/<int:application_id>", AssignRegistrarView.as_view()),

    # Registrar
    path("registrar/assigned", AssignedApplicationsListView.as_view()),
    path("registrar/approve/<int:application_id>", ApproveApplicationView.as_view()),
    path("registrar/reject/<int:application_id>", RejectApplicationView.as_view()),

   
]
