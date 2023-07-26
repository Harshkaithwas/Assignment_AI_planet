from django.shortcuts import render

# Create your views here.
from accounts.serializers import *
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from datetime import datetime, timedelta
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse


class OTPVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({"message": "Invalid email address"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"message": "User already verified"}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp == otp:
            user.is_verified = True
            user.save()
            return Response({"message": "OTP verification successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)




class ResendOTPView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        serializer = ResendOTPSerializer(data={"email": email})
        if serializer.is_valid():
            otp = serializer.save()
            response_data = {
                "message": "OTP resent for verification.",
                "email": email,
                "otp": otp
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_id = user.id
            response = {
                'message': 'Your Account Has Been Registered Successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user_id
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class SignInView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get('username')
        password = request.data.get("password")
        role = request.data.get("role")  # Add the role field for specifying Host or Participant

        # Check if any required field is missing
        if not (email or username) or not password or not role:
            missing_fields = []
            if not email and not username:
                missing_fields.append('email or username')
            if not password:
                missing_fields.append('password')
            if not role:
                missing_fields.append('role')

            response = {
                'success': False,
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': f"Please provide the following required fields: {', '.join(missing_fields)}.",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Check if both email and username are provided
        if email and username:
            response = {
                'success': False,
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': "Please provide either email or username, not both.",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Check if the role is valid
        if role.lower() not in ('host', 'participant'):
            response = {
                'success': False,
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': "Invalid role. Role must be either 'host' or 'participant'.",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user based on provided email or username
        if email:
            user = authenticate(email=email, password=password)
        else:
            user = authenticate(username=username, password=password)

        if user is not None:
            # Check if the role matches with the user's role
            if user.role.lower() != role.lower():
                response = {
                    'success': False,
                    'status code': status.HTTP_400_BAD_REQUEST,
                    'message': "Invalid role for this user.",
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            user_id = user.id
            response = {
                'success': True,
                'status code': status.HTTP_200_OK,
                'message': 'User logged in successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user_id
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'success': False,
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid credentials. Please correct them and try again',
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)



class SignOutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = {
                'success': 'True',
                'message': "Your account has been logged out successfully",
                'status code': status.HTTP_200_OK,
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'success': 'False',
                'message': "There is some problem while logging you out.",
                'status': status.HTTP_400_BAD_REQUEST
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsView(APIView):
    def get(self, request, pk):
        try:
            user_obj = Account.objects.get(id=pk)
            serializer = UserDetailsSerializer(user_obj, context={'request': request})
            return Response(serializer.data)
        except Account.DoesNotExist:
            return Response({
                'message': "Account not found", 
                'status': status.HTTP_404_NOT_FOUND
            })

class AccountProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user
        serializer = AccountProfileSerializer(user_profile)
        return Response(serializer.data)
    
    def put(self, request):
        user_profile = request.user
        serializer = AccountProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitKYCView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is authenticated and has the role of a Host
        if not user.is_authenticated or user.role.lower() != 'host':
            response = {
                'success': False,
                'status code': status.HTTP_401_UNAUTHORIZED,
                'message': "You are not authorized to submit KYC documents.",
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        kyc_document = request.FILES.get('kyc_document')

        # Check if the KYC document is provided
        if not kyc_document:
            response = {
                'success': False,
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': "Please provide the KYC document.",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Save the KYC document to the user's account
        user.kyc_document = kyc_document
        user.save()

        response = {
            'success': True,
            'status code': status.HTTP_200_OK,
            'message': "KYC document submitted successfully.",
        }
        return Response(response, status=status.HTTP_200_OK)
    



User = get_user_model()

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            return Response({'error': 'Please provide old_password, new_password, and confirm_password'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password'},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password changed successfully'},
                        status=status.HTTP_200_OK)



class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

        # Generate a reset token for the user
        token = default_token_generator.make_token(user)

        # Encode user ID and token to create the password reset link
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))

        # Construct the password reset link
        reset_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
        reset_link = request.build_absolute_uri(reset_link)

        # Send the password reset link to the user's email
        subject = 'Password Reset Link'
        message = f'Please click on the following link to reset your password: {reset_link}'
        from_email = 'your_email@example.com'  # Set your from email address here
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Password reset link sent to your email. Please check your inbox.'},
                        status=status.HTTP_200_OK)


class SetNewPasswordView(APIView):
    def put(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Please provide both new_password and confirm_password'},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)