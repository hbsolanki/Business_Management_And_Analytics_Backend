from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle

from apps.user.models import User
from apps.user.serializers import forget
from apps.user.tasks import send_username_email, send_otp_email
from apps.user.utils.forgot_password import mask_email, generate_otp

class ForgetPasswordThrottle(AnonRateThrottle):
    rate = "5/min"

class ForgetViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    throttle_classes = [ForgetPasswordThrottle]

    def get_serializer_class(self):
        if self.action == "validate_username":
            return forget.ValidateUsernameSerializer
        if self.action == "validate_otp":
            return forget.ValidateOTPSerializer
        if self.action == "reset":
            return forget.ResetPasswordSerializer
        if self.action == "forget_username":
            return forget.ForgetUsernameSerializer
        return None

    @action(detail=False, methods=["post"], url_path="password/validate-username")
    def validate_username(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        user = User.objects.filter(username=username).first()

        if not user or not user.email:
            return Response(
                {"message": "If the account exists, an OTP has been sent"},
                status=status.HTTP_200_OK,
            )

        otp = generate_otp()
        cache.set(f"fp:{username}", otp, timeout=180)

        send_otp_email.delay(
            to_email=user.email,
            otp=otp,
            purpose="password reset",
        )

        return Response(
            {"message": f"OTP sent to {mask_email(user.email)}"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="password/validate-otp")
    def validate_otp(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        otp = serializer.validated_data["otp"]

        if cache.get(f"fp:{username}") != otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.delete(f"fp:{username}")
        cache.set(f"fp_verified:{username}", True, timeout=120)

        return Response(
            {"message": "OTP verified"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="password/reset")
    def reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        if not cache.get(f"fp_verified:{username}"):
            return Response(
                {"error": "OTP not verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=username).first()
        if not user:
            return Response(
                {"error": "Invalid user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            return Response({"error": e.messages}, status=400)

        user.set_password(password)
        user.save()

        cache.delete(f"fp_verified:{username}")

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="username")
    def forget_username(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            send_username_email.delay(
                to_email=email,
                username=user.username,
            )

        return Response(
            {"message": "If the email exists, the username has been sent"},
            status=status.HTTP_200_OK,
        )
