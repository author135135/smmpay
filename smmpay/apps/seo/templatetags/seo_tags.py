from django import template
from smmpay.apps.seo.models import PageSeoInformation

register = template.Library()


@register.inclusion_tag(filename='seo/tags/seo_information.html', takes_context=True)
def render_head_meta_information(context, *args, **kwargs):
    """
    Render meta tags ONLY for head section
    """
    request = context['request']

    context = {
        'seo_obj': PageSeoInformation.get_for_url(request.path),
    }

    return context
