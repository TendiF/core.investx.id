from rest_framework.permissions import *
from enterprise.libs.rest_module.authentication import *
from django.utils.translation import gettext_lazy as _
from enterprise.structures.authentication.models import PhoneVerification, EmailVerification

class IsVerified(BasePermission):
    """
    Allows access only to authenticated users.
    """
    message = _('Please verify your email and phone number')

    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        if not is_authenticated:
            return False

        ev = EmailVerification.objects.filter(email=request.user.email).last()
        pv = PhoneVerification.objects.filter(phone_number=request.user.phone_number).last()

        pv_verified = pv.is_verified if pv else False
        ev_verified = ev.is_verified if ev else False

        if not pv_verified:
            return False
        if not ev_verified:
            return False

        return True