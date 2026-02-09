import requests
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from apps.user.models import User

from apps.business.models import Business

User = get_user_model()


class GoogleOAuthLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        auth_code = request.data.get("code")

        if not auth_code:
            return Response(
                {"error": "Google code required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Exchange Auth Code for ID Token
            token_endpoint = "https://oauth2.googleapis.com/token"
            payload = {
                'code': auth_code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': 'postmessage',  # 'postmessage'
            }

            # Request Google to swap code for token
            exchange_response = requests.post(token_endpoint, data=payload)
            exchange_data = exchange_response.json()

            # Check if exchange failed
            if "error" in exchange_data:
                return Response(
                    {"error": f"Google Exchange Error: {exchange_data.get('error_description')}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract the actual JWT ID Token
            google_id_token = exchange_data.get("id_token")

            # Now we can verify the token we just received
            idinfo = id_token.verify_oauth2_token(
                google_id_token,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,
            )

            email = idinfo["email"]
            name = idinfo.get("name", "")

            #Login or Create User
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": name,
                    "role":User.Role.OWNER,
                },
            )
            business=None
            if created:
                business = Business.objects.create()
                user.business = business
                user.save(update_fields=["business"])
            else:
                business=user.business
            refresh = RefreshToken.for_user(user)

            return Response({
                "business_id": business.id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print(f"Login Failed: {str(e)}")
            return Response(
                {"error": "Authentication Failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )