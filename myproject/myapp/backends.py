from django.contrib.auth.models import User as CustomUser
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(object):

    def authenticate(self,request,username=None, password=None, **kwargs):
        username = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=username)
        except User.MultipleObjectsReturned:
            user =User.objects.get(email=username).order_by('id').first()
        except User.DoesNotExist:
            return None
        if getattr(user, 'is_active') and user.check_password(password):
            return user
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None