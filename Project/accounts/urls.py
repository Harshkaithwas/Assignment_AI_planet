from django.urls import path, include
from . import views
from accounts.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView


urlpatterns = [

    path('sign_up/', RegistrationView.as_view(), name='register'),
    path('otp_verification/', OTPVerificationView.as_view(), name='otp_verification'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('sign_in/', SignInView.as_view(), name='signin'),
    path('sign_out/', SignOutView.as_view(), name='signout'),
    path('user/<int:pk>/', UserDetailsView.as_view(), name='user_details'),
    path('profile/', AccountProfileView.as_view(), name='account_profile'),
    path('submit_kyc/', SubmitKYCView.as_view(), name='submit_kyc'),
    path('change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset_password/', ResetPasswordView.as_view(), name='password_reset'),
    path('reset_password/<str:uidb64>/<str:token>/', SetNewPasswordView.as_view(), name='password_reset_confirm'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]
