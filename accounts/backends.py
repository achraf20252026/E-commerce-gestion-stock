# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # On essaie de trouver un utilisateur avec cet email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Si l'email n'existe pas, on laisse les autres backends (comme celui par défaut) essayer
            return None

        # On vérifie le mot de passe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None