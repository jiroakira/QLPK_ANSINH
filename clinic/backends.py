from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import re

UserModel = get_user_model()

pattern = r"(84|0[3|5|7|8|9])+([0-9]{8})\b"
def check_phone(phone_str):
    pat = re.compile(pattern)
    if re.fullmatch(pat, phone_str):
        return True
    else:
        return False

class CredentialsBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        if check_phone(username):
            kwargs = {'so_dien_thoai': username}
        else:
            kwargs = {'username': username}
        try:
            user = UserModel.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            print('hello')
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None