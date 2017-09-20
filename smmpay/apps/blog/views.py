from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.template import RequestContext
from .models import Post


class IndexView(ListView):
    template_name = 'blog/index.html'
    ajax_template_name = 'blog/parts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get(self, request, *args, **kwargs):
        result = super(IndexView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            template = get_template(self.ajax_template_name)
            context = RequestContext(self.request, result.context_data)

            return JsonResponse({
                'success': True,
                'data': template.render(context)
            })

        return result

    def get_queryset(self):
        return Post.published_objects.all()


class PostView(DetailView):
    template_name = 'blog/post.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.published_objects.all()

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)

        context['site_url'] = get_current_site(self.request)

        return context
