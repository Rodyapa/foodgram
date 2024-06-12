from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Invalid username format',
    code='Invalid_username'
)


class CantSubscribeMyselfValdiator:
    """Валидатор проверяет,
    что пользователь не пытается подписаться на самого себя."""

    requires_context = True

    def __call__(self, attrs, serializer):
        current_user = serializer.initial_data['user']
        target_user = serializer.initial_data['target_user']
        if current_user == target_user:
            raise ValidationError('Sorry you cannot leave '
                                  'more than one review for single a title')
