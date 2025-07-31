from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, UserRole, Services

class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.CharField(max_length=50)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username (email) already exists.")
        return value

    def validate_role(self, value):
        try:
            UserRole.objects.get(name=value)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError(f"Role '{value}' does not exist.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        role = UserRole.objects.get(name=validated_data['role'])
        UserProfile.objects.create(user=user, role=role)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class LogoutSerializer(serializers.Serializer):
    pass

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', allow_null=True)
    services = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Services.objects.all(), required=False)
    null_or_blank_fields = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'role', 'is_authenticated', 'full_name', 'phone_number', 'bio',
            'profile_picture', 'date_of_birth', 'location', 'website',
            'latitute', 'longitude', 'services', 'null_or_blank_fields'
        )

    def get_null_or_blank_fields(self, obj):
        fields = [
            'role', 'full_name', 'phone_number', 'bio', 'profile_picture',
            'date_of_birth', 'location', 'website', 'latitute', 'longitude'
        ]
        null_or_blank = [field for field in fields if getattr(obj, field, None) in (None, '')]
        if not obj.services.exists():
            null_or_blank.append('services')
        return null_or_blank

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile')

class UpdateProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(max_length=50, required=False)
    services = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Services.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = (
            'role', 'full_name', 'phone_number', 'bio',
            'profile_picture', 'date_of_birth', 'location', 'website',
            'latitute', 'longitude', 'services'
        )

    def validate_role(self, value):
        try:
            UserRole.objects.get(name=value)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError(f"Role '{value}' does not exist.")
        return value

    def update(self, instance, validated_data):
        role_name = validated_data.pop('role', None)
        if role_name:
            instance.role = UserRole.objects.get(name=role_name)
        services = validated_data.pop('services', None)
        if services is not None:
            instance.services.set(services)
        return super().update(instance, validated_data)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email exists.")
        return value