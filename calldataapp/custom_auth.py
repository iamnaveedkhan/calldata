
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from datetime import time

class TimeRestrictedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)

        if user is not None:
            if user.role is not 1:
                current_time = timezone.now().time()

                if not (time(10, 0) <= current_time <= time(19, 0)):
                    raise PermissionDenied("Login is allowed only between 10 am and 7 pm.")

        return user
