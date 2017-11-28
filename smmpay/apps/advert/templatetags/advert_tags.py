import re
import sys

from django import template
from django.utils.http import urlencode
from django.utils.html import mark_safe
from django.template.loader import get_template

from smmpay.apps.advert.models import Menu, Advert, ContentBlock

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


@register.simple_tag(takes_context=True)
def content_block(context, position, *args, **kwargs):
    output = ''
    request = context['request']

    for block in ContentBlock.objects.filter(position=position, enabled=True):
        # Check if block should be rendered on current page
        pages = block.pages.splitlines()
        render_block = False

        for page in pages:
            page = page.strip()

            if page == '*' or re.match(r'%s' % page, request.path) is not None:
                render_block = True

                break

        # Render block if previous step set `render_block` to True
        if render_block:
            default_template = 'advert/tags/content_block/%s_default.html' % position
            template_name = block.template_name or default_template

            try:
                block_template = get_template(template_name=template_name)
            except template.TemplateDoesNotExist:
                block_template = get_template(template_name=default_template)

            # Prepare default context for render
            block_context = {
                'request': request,
                'block_obj': block,
            }

            # Update default context by function if it provided and exists in current module
            if block.context_function and hasattr(sys.modules[__name__], block.context_function):
                context_function = getattr(sys.modules[__name__], block.context_function)

                block_context.update(context_function(context, *args, **kwargs))

            output += block_template.render(block_context)

    return mark_safe(output)


def recommended_adverts(context, order_by='-pk', count=4, *args, **kwargs):
    block_context = {
        'recommended_adverts': Advert.published_objects.filter(**kwargs).order_by(order_by)[:count]
    }

    return block_context
