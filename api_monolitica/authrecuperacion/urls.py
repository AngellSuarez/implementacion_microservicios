from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


from .views.auth import LoginView, LogoutView, user_info, RegistroClienteView

from .views.solicitar_codigo import SolicitarCodigoRecuperacionView
from .views.confirmar_codigo import ConfirmarCodigoRecuperacionView
from .views.cambiar import cambiar_password  



router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # Auth URLs
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegistroClienteView.as_view(), name='register_cliente'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', user_info, name='user_info'),
    path('password/reset-request/',SolicitarCodigoRecuperacionView.as_view(),name='reset_request'),
    path('password/reset-confirm/',ConfirmarCodigoRecuperacionView.as_view(),name='reset_confirm'),
    path('password/cambiar/', cambiar_password, name='cambiar_password'),
]
