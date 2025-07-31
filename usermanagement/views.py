from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import SignupSerializer, LoginSerializer, LogoutSerializer, UserSerializer, UpdateProfileSerializer, ForgotPasswordSerializer
from django.http import HttpResponse


def root(request):
    return HttpResponse("Welcome to KajBondhu User Management API")




class SignupView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Sign up a new user with email, password, and role (username is set to email).",
        request_body=SignupSerializer,
        responses={
            201: openapi.Response(
                description="Account created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="account created successfully"),
                        'token': openapi.Schema(type=openapi.TYPE_STRING, example="a3a00203b7312ef4e7823ba7bc6cfdcbe1b16f67982354c44fb0a1684c621c16")
                    }
                )
            ),
            400: 'Invalid input'
        }
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            _, token = AuthToken.objects.create(user)
            return Response({
                'message': 'account created successfully',
                'token': token,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Log in a user with email and password. Blocks login if user is already logged in on another device.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="login successfully"),
                        'token': openapi.Schema(type=openapi.TYPE_STRING, example="a3a00203b7312ef4e7823ba7bc6cfdcbe1b16f67982354c44fb0a1684c621c16")
                    }
                )
            ),
            401: 'Invalid credentials or already logged in',
            400: 'Invalid input'
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                existing_tokens = AuthToken.objects.filter(user=user)
                if existing_tokens.exists():
                    return Response({
                        'error': 'Not you already log in another device, please logout from this and after that try again'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                _, token = AuthToken.objects.create(user)
                return Response({
                    'message': 'login successfully',
                    'token': token,
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Log out a user by deleting their active token.",
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="logout successfully")
                    }
                )
            ),
            401: 'Unauthorized'
        }
    )
    def post(self, request):
        AuthToken.objects.filter(user=request.user).delete()
        return Response({
            'message': 'logout successfully'
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Retrieve authenticated user's profile details with null or blank fields list.",
        responses={
            200: openapi.Response(
                description="Profile details",
                schema=UserSerializer
            ),
            401: 'Unauthorized'
        }
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Update authenticated user's profile (all fields optional).",
        request_body=UpdateProfileSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="profile updated successfully")
                    }
                )
            ),
            400: 'Invalid input',
            401: 'Unauthorized'
        }
    )
    def patch(self, request):
        profile = request.user.userprofile
        serializer = UpdateProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'profile updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Send a password reset link to the user's email.",
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Reset link sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, example="password reset link sent to your email")
                    }
                )
            ),
            400: 'Invalid input'
        }
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{request.build_absolute_uri('/')}reset-password/{uid}/{token}/"
            subject = "Password Reset Request"
            message = f"Click the link to reset your password: {reset_url}"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'password reset link sent to your email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)