
from django.contrib.auth import get_user_model

from management.models import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self,  email=None, password=None):
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(Q(email__iexact=email))
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None

    def get_user(self,id):
        try:
            return get_user_model().objects.get(pk=id)
        except get_user_model().DoesNotExist:
            return None
