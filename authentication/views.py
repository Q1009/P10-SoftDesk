from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Inscription : vérifie l'âge (>= 15 ans) et recueille les consentements RGPD."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Accès, rectification et suppression (droit à l'oubli) du profil utilisateur."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {'detail': 'Votre compte et toutes vos données ont été supprimés.'},
            status=status.HTTP_204_NO_CONTENT,
        )
