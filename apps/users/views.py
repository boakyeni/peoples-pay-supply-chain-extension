from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
import requests
from rest_framework_simplejwt.tokens import RefreshToken

CENTRAL_AUTH_URL = "https://central-auth-service-url.com"

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("username")
    password = request.data.get("password")

    # Send credentials to centralized service
    response = requests.post(f"{CENTRAL_AUTH_URL}/validate-credentials",
                             data={"email": email, "password": password})
    
    if response.status_code == 200:
        # If valid, issue JWT token
        token = RefreshToken()
        data = response.json()
        token["merchant_id"] = data['registrationNumber']
        token['merchant_name'] = data["merchant_name"]
        
        return Response({
            "refresh": str(token),
            "access": str(token.access_token),
        })
    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    user_data = {
        "email": request.data.get("email"),
        "password": request.data.get("password"),
        # Add other fields as needed
    }

    # Send user data to centralized service for account creation
    response = requests.post(f"{CENTRAL_AUTH_URL}/create-account", data=user_data)
    
    if response.status_code == 200:
        # If account creation successful, issue JWT token
        token = RefreshToken()
        data = response.json()
        token["merchant_id"] = data['registrationNumber']
        return Response({
            "refresh": str(token),
            "access": str(token.access_token),
        })
    return Response({"detail": "Account creation failed"}, status=status.HTTP_400_BAD_REQUEST)


