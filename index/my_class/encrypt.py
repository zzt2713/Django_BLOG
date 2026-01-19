import hashlib
from django.conf import settings

def md5(pwd):
    obj=hashlib.md5(settings.SECRET_KEY.encode("utf8"))
    obj.update(pwd.encode('utf-8'))
    return obj.hexdigest()