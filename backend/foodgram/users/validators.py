from django.core.validators import RegexValidator

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Invalid username format',
    code='Invalid_username'
)


