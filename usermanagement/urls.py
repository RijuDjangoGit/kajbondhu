from django.urls import path
from django.urls import path
from .views import SignupView, LoginView, LogoutView, ProfileView, UpdateProfileView, ForgotPasswordView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

app_name = 'usermanagement'

schema_view = get_schema_view(
    openapi.Info(
        title="User Management API",
        default_version='v1',
        description="API for user signup, login, logout, profile management, and password reset with Knox token authentication",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(),
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]