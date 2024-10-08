from django.db.models import Sum
from django.http import HttpResponse
from recipes.models import IngredientPerRecipe
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import os
from django.conf import settings


def create_ingredients_list(request):
    final_list = {}
    ingredients = IngredientPerRecipe.objects.filter(
        recipe__in_cart__user=request.user).annotate(
            total_amount=Sum("amount")).order_by('recipe__name').values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
    for item in ingredients:
        name = item[0]
        final_list[name] = {
            'measurement_unit': item[1],
            'total_amount': item[2]
        }
    return final_list


def make_pdf_file_of_ingredients(final_list):
    # Check for the correct font path in production
    font_path = os.path.join(settings.BASE_DIR, 'Lato-Regular.ttf')

    pdfmetrics.registerFont(TTFont('Lato-Regular', font_path))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_list.pdf"')
    page = canvas.Canvas(response)
    page.setFont('Lato-Regular', size=18)
    page.drawString(200, 800, 'Список ингредиентов')

    page.setFont('Lato-Regular', size=16)
    height = 750
    for i, (name, data) in enumerate(final_list.items(), 1):
        page.drawString(75, height,
                        f'{i}.  {name} - {data["total_amount"]}, '
                        f'{data["measurement_unit"]}')
        height -= 25

    page.showPage()
    page.save()

    return response
