from string import hexdigits

from django.core.exceptions import ValidationError


class HexColorValidator:
    """Проверяет что цвет соответсвует формату
    записи цвета в шестнадцатиричном формате"""

    def __call__(self, color):
        color = color.strip(" #")
        if len(color) not in (3, 6):
            raise ValidationError(
                f"Код цвета {color} не правильной длины ({len(color)})."
            )
        if not set(color).issubset(hexdigits):
            raise ValidationError(f"{color} не шестнадцатиричное значение.")
