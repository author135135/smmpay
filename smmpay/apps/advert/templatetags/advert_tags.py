import re
import sys
import random

from django import template
from django.utils.html import mark_safe
from django.http import QueryDict
from django.template.loader import get_template

from smmpay.apps.advert.models import Menu, Advert, ContentBlock

register = template.Library()


@register.simple_tag
def build_querystring(params, exclude='', **kwargs):
    final_params = QueryDict(mutable=True)

    exclude = exclude.split(',')

    if isinstance(params, QueryDict):
        params = dict(params)

    for key, value in params.items():
        if key not in exclude:
            if isinstance(value, list):
                for item in value:
                    final_params.update({key: item})
            else:
                final_params.update({key: value})

    for key, value in kwargs.items():
        if isinstance(value, list):
            for item in value:
                final_params.update({key: item})
        else:
            final_params.update({key: value})

    return final_params.urlencode()


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


def menu(context, *args, **kwargs):
    block_context = {
        'menu': Menu.objects.filter(position=args[0]).prefetch_related('menu_items')
    }

    return block_context


def recommended_adverts(context, order_by='-pk', count=4, *args, **kwargs):
    # Get VIP adverts first
    vip_advert_ids = [obj['pk'] for obj in Advert.objects.filter(
        special_status=Advert.ADVERT_SPECIAL_STATUS_VIP).values('pk')]
    sample_count = count if len(vip_advert_ids) >= count else len(vip_advert_ids)
    filter_ids = random.sample(vip_advert_ids, sample_count)

    adverts = list(Advert.objects.filter(id__in=filter_ids))

    # Get adverts from main list if less than `count` adverts have vip status
    if len(adverts) < count:
        count = count - len(adverts)

        adverts_qs = Advert.published_objects.filter(**kwargs)

        if adverts:
            adverts_qs = adverts_qs.exclude(id__in=[advert.pk for advert in adverts])

        adverts_qs = adverts_qs.order_by(order_by)[:count]

        for advert in adverts_qs:
            adverts.append(advert)

    block_context = {
        'recommended_adverts': adverts
    }

    return block_context
