from django.core.validators import MinLengthValidator
from rest_framework import serializers
from accounts.models import Account, AccountProfileModel
from django.core.mail import send_mail
import random
import string





class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def generate_otp(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    def send_verification_email(self, email, otp):
        subject = 'Email Verification OTP'
        message = f'Your OTP for email verification is: {otp}'
        from_email = 'rc261121@example.com'  # Set your from email address here
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

    def validate_email(self, email):
        if Account.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email

    def save(self, **kwargs):
        email = self.validated_data['email']
        otp = self.generate_otp()
        self.send_verification_email(email, otp)

        return {'email': email, 'otp': otp}

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        if not Account.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is not registered.")
        return email

    def save(self, **kwargs):
        email = self.validated_data['email']
        otp_serializer = EmailVerificationSerializer(data={'email': email})
        otp_serializer.is_valid(raise_exception=True)
        validated_data = otp_serializer.save()
        return validated_data['otp']

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    otp = serializers.CharField(max_length=6, validators=[MinLengthValidator(6)], write_only=True, required=False)
    role = serializers.ChoiceField(choices=Account.ROLE_CHOICES, required=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'password', 'password2', 'otp', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, email):
        if Account.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email

    def save(self, **kwargs):
        email = self.validated_data['email']
        username = self.validated_data['username']
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        otp = self.validated_data.get('otp')
        role = self.validated_data['role']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})

        if not otp:
            # Use the EmailVerificationSerializer to send verification email and generate OTP
            email_serializer = EmailVerificationSerializer(data={'email': email})
            email_serializer.is_valid(raise_exception=True)
            validated_data = email_serializer.save()
            otp = validated_data['otp']

        account = Account(
            email=email,
            username=username,
            is_verified=False,
            role=role,
        )

        account.set_password(password)
        account.otp = otp
        account.save()

        return account



class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'gender', 'dob', 'profile_pic', 'banner_pic', 'phone', 'country_code']


class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'gender', 'dob', 'profile_pic', 'banner_pic', 'phone', 'country_code']


