import logging

from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, View, ListView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import get_user_model
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import get_language_from_request
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from . import forms as advert_forms
from .models import Advert, AdvertSocialAccount, Phrase, SocialNetwork, FavoriteAdvert, Discussion


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdvertFilterMixin(object):
    filters = {
        'search_query': ['title__icontains', 'description__icontains'],
        'region': ['social_account__region__slug'],
        'category': ['category__slug'],
        'price_min': ['price__gte'],
        'price_max': ['price__lte'],
        'subscribers_min': ['social_account__subscribers__gte'],
        'subscribers_max': ['social_account__subscribers__lte'],
        'social_network': ['social_account__social_network__code'],
    }

    def get_queryset(self):
        qs = super(AdvertFilterMixin, self).get_queryset()

        filter_form = advert_forms.FilterForm(self.request.GET)

        for item in self.filters:
            if not filter_form.has_error(item) and filter_form.cleaned_data.get(item, None):
                search_value = filter_form.cleaned_data[item]
                qs_query = None

                for expression in self.filters[item]:
                    if qs_query is None:
                        qs_query = Q(**{expression: search_value})
                    else:
                        qs_query |= Q(**{expression: search_value})

                if qs_query is not None:
                    qs = qs.filter(qs_query)

        # Set filter by first social network if not checked
        social_network = filter_form.cleaned_data.get('social_network', '')

        if not social_network:
            try:
                obj = SocialNetwork.objects.first()
            except SocialNetwork.DoesNotExist:
                return qs

            qs = qs.filter(social_account__social_network=obj)

        return qs


class AdvertSubFormMixin(object):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.sub_object = self.get_sub_object()

        return super(AdvertSubFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.sub_object = self.get_sub_object()

        form = self.get_form()
        sub_form = self.get_sub_form()

        if form.is_valid() and sub_form.is_valid():
            return self.form_valid(form, sub_form)
        else:
            return self.form_invalid(form, sub_form)

    def get_context_data(self, **kwargs):
        if 'sub_form' not in kwargs:
            kwargs['sub_form'] = self.get_sub_form()

        return super(AdvertSubFormMixin, self).get_context_data(**kwargs)

    def form_valid(self, form, sub_form):
        self.object = form.save()
        self.sub_object = sub_form.save()

        return super(AdvertSubFormMixin, self).form_valid(form)

    def form_invalid(self, form, sub_form):
        return self.render_to_response(self.get_context_data(form=form, sub_form=sub_form))

    def get_sub_form(self):
        advert_type = self.model.get_default_advert_type()
        advert_type = ''.join(map(lambda item: item.capitalize(), advert_type.split('_')))

        sub_form_class = 'Advert{}Form'.format(advert_type)

        return getattr(advert_forms, sub_form_class)(self.request.POST or None, self.request.FILES or None,
                                                     instance=self.get_sub_object())

    def get_sub_object(self):
        sub_object = None

        if isinstance(self.object, Advert):
            advert_type = self.model.get_default_advert_type()
            sub_object = getattr(self.object, advert_type)

        return sub_object


class IndexView(AdvertFilterMixin, ListView):
    template_name = 'advert/index.html'
    ajax_items_template_name = 'advert/parts/advert_list.html'
    context_object_name = 'adverts'
    model = Advert
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            return JsonResponse({
                'success': True,
                'data': render_to_string(self.ajax_items_template_name, response.context_data, request),
            })

        return response

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['filter_form'] = advert_forms.FilterForm(self.request.GET or None)
        context['social_networks'] = SocialNetwork.objects.all()

        selected_social_network = self.request.GET.get('social_network', None)

        if selected_social_network is None or not selected_social_network:
            social_network_obj = SocialNetwork.objects.values('code').first()

            if social_network_obj is not None:
                selected_social_network = social_network_obj.get('code')

        context['selected_social_network'] = selected_social_network

        return context

    def get_queryset(self):
        qs = super(IndexView, self).get_queryset()
        qs &= Advert.published_objects.get_extra_queryset(select_items=['in_favorite'],
                                                          select_params=[self.request.user.pk])

        return qs


class AdvertView(DetailView):
    template_name = 'advert/advert.html'
    context_object_name = 'advert'
    model = Advert

    def get_context_data(self, **kwargs):
        context = super(AdvertView, self).get_context_data(**kwargs)

        context['prev_advert'] = self.model.published_objects.filter(pk__lt=self.object.pk).first()
        context['next_advert'] = self.model.published_objects.filter(pk__gt=self.object.pk).order_by('pk').first()

        context['message_form'] = advert_forms.DiscussionMessageForm()

        if self.object.author == self.request.user and self.object.status != Advert.ADVERT_STATUS_PUBLISHED:
            messages.add_message(self.request, messages.INFO, _('Advert on moderation. '
                                                                'It will be published on site after this.'))

        return context

    def get_queryset(self):
        qs = super(AdvertView, self).get_queryset()
        qs &= Advert.objects.get_extra_queryset(select_items=['in_favorite'], select_params=[self.request.user.pk])

        qs = qs.filter(Q(enabled_by_author=True, status=Advert.ADVERT_STATUS_PUBLISHED) |
                       Q(author=self.request.user.pk))

        return qs


class FavoriteAdvertView(View):
    def post(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            in_favorite = None
            advert_id = request.POST.get('advert_id', None)

            if advert_id is not None:
                try:
                    advert = Advert.published_objects.get(pk=advert_id)

                    try:
                        favorite = FavoriteAdvert.objects.get(advert=advert, user=request.user)
                        favorite.delete()

                        in_favorite = False
                    except FavoriteAdvert.DoesNotExist:
                        favorite = FavoriteAdvert(advert=advert, user=request.user)
                        favorite.save()

                        in_favorite = True

                    response_data = {
                        'success': True,
                        'in_favorite': in_favorite
                    }
                except Advert.DoesNotExist:
                    pass

        return JsonResponse(response_data)


class AdvertSendMessageView(View):
    def post(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            try:
                advert = Advert.published_objects.get(pk=kwargs['pk'])

                if advert.author != request.user:
                    try:
                        discussion = Discussion.objects.get(advert=advert, users=self.request.user)
                    except Discussion.DoesNotExist:
                        discussion_users = [self.request.user, advert.author]

                        discussion = Discussion.create_discussion(advert, discussion_users)

                    form = advert_forms.DiscussionMessageForm(self.request.POST)

                    if form.is_valid():
                        discussion.add_message(self.request.user, form.cleaned_data['message'])

                        response_data['success'] = True
                    else:
                        response_data['errors'] = form.errors
            except Advert.DoesNotExist:
                pass

        return JsonResponse(response_data)


class AdvertAddViewView(View):
    def get(self, *args, **kwargs):
        response_data = {
            'success': False
        }

        try:
            advert = Advert.published_objects.get(pk=kwargs['pk'])

            response_data['success'] = advert.add_view(self.request)
        except Advert.DoesNotExist:
            pass

        return JsonResponse(response_data)


class AdvertAddView(LoginRequiredMixin, AdvertSubFormMixin, CreateView):
    template_name = 'advert/advert_add.html'
    form_class = advert_forms.AdvertForm
    model = Advert

    def get_context_data(self, **kwargs):
        context = super(AdvertAddView, self).get_context_data(**kwargs)

        phrase_obj = Phrase.get_rand_phrase(get_language_from_request(self.request))

        if phrase_obj is not None:
            confirmation_code = phrase_obj.phrase
        else:
            confirmation_code = get_random_string(length=32)

        self.request.session['advert_confirmation_code'] = confirmation_code

        context['advert_confirmation_code'] = confirmation_code

        return context

    def form_valid(self, form, sub_form):
        advert = form.save(False)
        advert.author = self.request.user

        advert.save()

        advert_additional = sub_form.save(False)
        advert_additional.advert = advert
        advert_additional.confirmation_code = self.request.session['advert_confirmation_code']

        advert_additional.save()

        messages.add_message(self.request, messages.SUCCESS, _('Advert has been successfully added. '
                                                               'It will be published on the site after the moderation. '
                                                               'Usually it takes from 20 to 50 minutes.'))

        del self.request.session['advert_confirmation_code']

        return super(AdvertAddView, self).form_valid(form, sub_form)

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('advert:index'))

    def get_object(self, queryset=None):
        return None


class AdvertSocialAccountInfoView(View):
    def get(self, *args, **kwargs):
        account_link = self.request.GET.get('account_link', None)
        response_data = {
            'success': False
        }

        if account_link is None:
            return JsonResponse(response_data)

        try:
            client = AdvertSocialAccount.get_api_connector(account_link=account_link)
            account_info = client.get_account_info()

            response_data['success'] = True
            response_data['fields'] = {
                'title': account_info.get('title', None),
                'subscribers': account_info.get('subscribers', None),
                'external_logo': account_info.get('logo', None)
            }
        except Exception as e:
            logger = logging.getLogger('db')
            logger.exception(e)

            return JsonResponse(response_data)

        return JsonResponse(response_data)


class AdvertEditView(LoginRequiredMixin, AdvertSubFormMixin, UpdateView):
    template_name = 'advert/advert_edit.html'
    form_class = advert_forms.AdvertForm
    model = Advert
    context_object_name = 'advert'

    def form_valid(self, form, sub_form):
        messages.add_message(self.request, messages.SUCCESS, _('Advert successfully edited'))

        return super(AdvertEditView, self).form_valid(form, sub_form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_queryset(self):
        return super(AdvertEditView, self).get_queryset().filter(author=self.request.user)


class UserAdvertsView(IndexView):
    template_name = 'advert/user_adverts.html'

    def get_context_data(self, **kwargs):
        context = super(UserAdvertsView, self).get_context_data(**kwargs)

        user_model = get_user_model()

        context['user_obj'] = user_model.objects.get(pk=self.kwargs['pk'])
        context['user_adverts_count'] = Advert.published_objects.filter(author=self.kwargs['pk']).count()

        return context

    def get_queryset(self):
        return super(UserAdvertsView, self).get_queryset().filter(author=self.kwargs['pk'])
