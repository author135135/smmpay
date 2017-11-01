from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .models import Post


class IndexView(ListView):
    template_name = 'blog/index.html'
    ajax_template_name = 'blog/parts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            return JsonResponse({
                'success': True,
                'data': render_to_string(self.ajax_template_name, response.context_data, request),
            })

        return response

    def get_queryset(self):
        return Post.published_objects.all()


class PostView(DetailView):
    template_name = 'blog/post.html'
    context_object_name = 'post'
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def get_queryset(self):
        return Post.published_objects.all()

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)

        context['site_url'] = get_current_site(self.request)

        return context
