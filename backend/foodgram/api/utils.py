from django.db.models import Sum
from django.http import HttpResponse
from recipes.models import IngredientPerRecipe
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_ingredients_list(request):
    final_list = {}
    ingredients = IngredientPerRecipe.objects.filter(
        recipe__shopingcart__user=request.user).values_list(
        'ingredient__name', 'ingredient__measurement_unit',
        'amount').annotate(amount=Sum("amount")).order_by('name')
    for item in ingredients:
        name = item[0]
        final_list[name] = {
            'measurement_unit': item[1],
            'amount': item[2]
        }
    return final_list


def make_pdf_file_of_ingredients(final_list):
    pdfmetrics.registerFont(
        TTFont('Lato-Regular', 'Lato-Regular.ttf', 'UTF-8'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_list.pdf"')
    page = canvas.Canvas(response)
    page.setFont('Lato-Regular', size=18)
    page.drawString(200, 800, 'Список ингредиентов')
    page.setFont('Lato-Regular', size=16)
    height = 750
    for i, (name, data) in enumerate(final_list.items(), 1):
        page.drawString(75, height, (f'{i}.  {name} - {data["amount"]}, '
                                     f'{data["measurement_unit"]}'))
        height -= 25
    page.showPage()
    page.save()
    return response
