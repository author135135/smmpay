from django import template
from django.utils.http import urlencode
from django.utils.html import mark_safe
from django.template.loader import get_template

from smmpay.apps.advert.models import Menu

register = template.Library()


@register.simple_tag(takes_context=True)
def menu(context, position=None, *args, **kwargs):
    output = ''

    try:
        objects = Menu.objects.filter(position=position).prefetch_related('menu_items')
    except Menu.DoesNotExist:
        raise template.TemplateSyntaxError("Parameter `position` should be a valid menu position")

    if objects is not None:
        for menu in objects:
            # Getting a menu template
            template_name = 'advert/tags/%s_menu.html' % position

            try:
                menu_template = get_template(template_name=template_name)
            except template.TemplateDoesNotExist:
                menu_template = get_template(template_name='advert/tags/default_menu.html')

            output += menu_template.render({
                'menu': menu,
                'request': context['request']
            })

    return mark_safe(output)


@register.simple_tag
def build_querystring(params, exclude='', **kwargs):
    final_params = {}

    exclude = exclude.split(',')

    for key, value in params.items():
        if key not in exclude:
            final_params[key] = value

    for key, value in kwargs.items():
        final_params[key] = value

    return urlencode(final_params)
