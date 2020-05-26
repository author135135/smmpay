import logging

from django.http import JsonResponse, Http404
from django.views.generic import CreateView, UpdateView, View, ListView, DetailView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import get_user_model
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.db import transaction
from django.db.models import Q, Case, When, Sum, IntegerField
from django.utils.translation import ugettext_lazy as _

from smmpay.apps.seo.models import PageSeoInformation
from smmpay.apps.advert.templatetags.advert_tags import recommended_adverts

from . import forms as advert_forms
# from .models import Advert, AdvertSocialAccount, Phrase, SocialNetwork, FavoriteAdvert, Discussion
from .models import Advert, AdvertSocialAccount, Phrase, SocialNetwork, FavoriteAdvert


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdvertFilterMixin(object):
    """
    Check this mixin after creating user's adverts page
    """
    filters = {
        'search_query': ['title__icontains', 'description__icontains'],
        'category': ['category__slug__in'],
        'service': ['social_account__social_account_services__social_network_service__in'],
        'price_min': ['min_price__gte'],
        'price_max': ['max_price__lte'],
        'subscribers_min': ['social_account__subscribers__gte'],
        'subscribers_max': ['social_account__subscribers__lte'],
    }

    def get(self, request, *args, **kwargs):
        if 'social_network' in kwargs:
            try:
                self._social_network = SocialNetwork.objects.get(code=kwargs['social_network'])
            except SocialNetwork.DoesNotExist:
                raise Http404()
        else:
            self._social_network = SocialNetwork.objects.first()

        response = super(AdvertFilterMixin, self).get(request, *args, **kwargs)

        if request.is_ajax():
            json_data = {
                'success': True,
                'data': render_to_string(self.ajax_items_template_name, response.context_data, request),
                'items_count': response.context_data['paginator'].count,
                'service': self._get_filter_form().fields['service'].choices,
                'page_seo_information': {}
            }

            page_seo_information = PageSeoInformation.get_for_url(request.path)

            if page_seo_information is not False:
                json_data['page_seo_information']['meta_title'] = page_seo_information.meta_title
                json_data['page_seo_information']['meta_description'] = page_seo_information.meta_description
                json_data['page_seo_information']['meta_keywords'] = page_seo_information.meta_keywords

            return JsonResponse(json_data)

        return response

    def get_queryset(self, *args, **kwargs):
        qs = super(AdvertFilterMixin, self).get_queryset()

        filter_form = self._get_filter_form()
        sort_by = filter_form.fields['sort_by'].initial

        if filter_form.is_bound:
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

            sort_by_value = filter_form.cleaned_data.get('sort_by', None)

            if sort_by_value:
                sort_by = sort_by_value

        qs &= Advert.published_objects.get_extra_queryset(select_items=['in_favorite'],
                                                          select_params=[self.request.user.pk])

        qs = qs.order_by('-special_status', sort_by)

        return qs

    def get_context_data(self, **kwargs):
        context = super(AdvertFilterMixin, self).get_context_data(**kwargs)

        context['filter_form'] = self._get_filter_form()

        try:
            context['social_networks'] = SocialNetwork.objects.all()
            context['selected_social_network'] = self._social_network
        except (SocialNetwork.DoesNotExist, AttributeError):
            pass

        return context

    def _get_filter_form(self, *args, **kwargs):
        if not hasattr(self, 'filter_form'):
            self.filter_form = advert_forms.FilterForm(data=self.request.GET or None,
                                                       selected_social_network=self._social_network)

        return self.filter_form


class AdvertSubFormsMixin(object):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.social_account_object = self.get_social_account_object()

        return super(AdvertSubFormsMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.social_account_object = self.get_social_account_object()

        form = self.get_form()
        advert_type_form = self.get_advert_type_form()
        advert_service_formset = self.get_advert_service_formset()

        if advert_service_formset.is_valid() and form.is_valid() and advert_type_form.is_valid():
            return self.form_valid(form, advert_type_form, advert_service_formset)
        else:
            return self.form_invalid(form, advert_type_form, advert_service_formset)

    def get_context_data(self, **kwargs):
        if 'advert_type_form' not in kwargs:
            kwargs['advert_type_form'] = self.get_advert_type_form()

        if 'advert_service_formset' not in kwargs:
            kwargs['advert_service_formset'] = self.get_advert_service_formset()

        return super(AdvertSubFormsMixin, self).get_context_data(**kwargs)

    def form_valid(self, form, advert_type_form, advert_service_formset):
        self.object = form.save()
        self.social_account_object = advert_type_form.save()

        advert_service_formset.save()

        return super(AdvertSubFormsMixin, self).form_valid(form)

    def form_invalid(self, form, advert_type_form, advert_service_formset):
        return self.render_to_response(self.get_context_data(form=form, advert_type_form=advert_type_form,
                                                             advert_service_formset=advert_service_formset))

    def get_advert_type_form(self):
        advert_type = self.model.get_default_advert_type()
        advert_type = ''.join(map(lambda item: item.capitalize(), advert_type.split('_')))

        advert_type_form_class = 'Advert{}Form'.format(advert_type)

        return getattr(advert_forms, advert_type_form_class)(self.request.POST or None, self.request.FILES or None,
                                                             instance=self.get_social_account_object(),
                                                             request=self.request)

    def get_advert_service_formset(self):
        return advert_forms.AdvertServiceFormSetFactory(self.request.POST or None,
                                                        instance=self.get_social_account_object(),
                                                        form_kwargs={'post_data': self.request.POST})

    def get_social_account_object(self):
        social_account_object = None

        if isinstance(self.object, Advert):
            advert_type = self.model.get_default_advert_type()
            social_account_object = getattr(self.object, advert_type)

        return social_account_object


class IndexView(ListView):
    template_name = 'advert/index.html'
    ajax_items_template_name = 'advert/parts/advert_list_home.html'
    context_object_name = 'adverts'
    model = Advert
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['social_networks'] = SocialNetwork.objects.annotate(adverts_count=Sum(
            Case(
                When(Q(social_accounts__advert__status=Advert.ADVERT_STATUS_PUBLISHED) &
                     Q(social_accounts__advert__enabled_by_author=True), then=1),
                default=0, output_field=IntegerField()
            )
        ))
        context['site'] = get_current_site(self.request)

        return context

    def get_queryset(self, *args, **kwargs):
        return super(IndexView, self).get_queryset().filter(special_status=self.model.ADVERT_SPECIAL_STATUS_VIP)


class AdvertView(DetailView):
    template_name = 'advert/advert.html'
    context_object_name = 'advert'
    model = Advert

    def get_context_data(self, **kwargs):
        context = super(AdvertView, self).get_context_data(**kwargs)

        context['prev_advert'] = self.model.simple_published_objects.filter(pk__lt=self.object.pk).first()
        context['next_advert'] = self.model.simple_published_objects.filter(pk__gt=self.object.pk).order_by(
            'pk').first()

        # context['message_form'] = advert_forms.DiscussionMessageForm()

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
            advert_id = request.POST.get('advert_id', None)

            if advert_id is not None:
                try:
                    advert = Advert.published_objects.get(pk=advert_id)

                    try:
                        favorite = FavoriteAdvert.objects.get(advert=advert, user=request.user)
                        favorite.delete()
                    except FavoriteAdvert.DoesNotExist:
                        favorite = FavoriteAdvert(advert=advert, user=request.user)
                        favorite.save()

                    response_data = {
                        'success': True
                    }
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


class AdvertAddView(LoginRequiredMixin, AdvertSubFormsMixin, CreateView):
    template_name = 'advert/advert_add.html'
    form_class = advert_forms.AdvertForm
    model = Advert

    @transaction.atomic
    def form_valid(self, form, advert_type_form, advert_service_formset):
        advert = form.save(False)
        advert.author = self.request.user
        advert.social_account = advert_type_form.save(False)
        advert.save()

        advert.social_account.advert = advert
        advert.social_account.save()

        advert_service_formset.instance = advert.social_account
        advert_service_formset.save()

        messages.add_message(self.request, messages.SUCCESS, _('Advert has been successfully added. '
                                                               'It will be published on the site after the moderation. '
                                                               'Usually it takes from 20 to 50 minutes.'))

        return super(AdvertAddView, self).form_valid(form, advert_type_form, advert_service_formset)

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('advert:index'))

    def get_object(self, queryset=None):
        return None


class AdvertSocialAccountInfoView(View):
    def get(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            account_link = self.request.GET.get('account_link', None)

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


class AdvertSocialAccountServicesView(View):
    def get(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            account_link = self.request.GET.get('account_link', None)

            if account_link is None:
                return JsonResponse(response_data)

            social_network = SocialNetwork.get_social_network(account_link)

            if social_network is None:
                return JsonResponse(response_data)

            response_data['success'] = True
            response_data['services'] = list(social_network.services.values_list('pk', 'title'))

        return JsonResponse(response_data)


class AdvertSocialAccountConfirmView(View):
    def post(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            account_link = request.POST.get('account_link', None)
            confirm_code = request.POST.get('confirm_code', None)

            if account_link is None or confirm_code is None:
                return JsonResponse(response_data)

            social_network = SocialNetwork.get_social_network(account_link)

            if social_network is None:
                return JsonResponse(response_data)

            try:
                parser = AdvertSocialAccount.get_parser(social_network.code)
                confirmed = parser.get_account_confirmation(url=account_link, code=confirm_code)
            except Exception as e:
                confirmed = False

                logger = logging.getLogger('db')
                logger.exception(e)

            response_data['success'] = True
            response_data['confirmed'] = bool(confirmed)

            request.session['social_account_confirm_link'] = account_link
            request.session['social_account_confirm_status'] = response_data['confirmed']

        return JsonResponse(response_data)


class AdvertEditView(LoginRequiredMixin, AdvertSubFormsMixin, UpdateView):
    template_name = 'advert/advert_edit.html'
    form_class = advert_forms.AdvertForm
    model = Advert
    context_object_name = 'advert'

    def form_valid(self, form, advert_type_form, advert_service_formset):
        messages.add_message(self.request, messages.SUCCESS, _('Advert successfully edited'))

        return super(AdvertEditView, self).form_valid(form, advert_type_form, advert_service_formset)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_queryset(self):
        return super(AdvertEditView, self).get_queryset().filter(author=self.request.user)


class UserAdvertsView(AdvertFilterMixin, ListView):
    template_name = 'advert/user_adverts.html'
    ajax_items_template_name = 'advert/parts/advert_list.html'
    context_object_name = 'adverts'
    model = Advert
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self._user = None

        user_model = get_user_model()

        try:
            self._user = user_model.objects.get(pk=self.kwargs['pk'], is_active=True)
        except user_model.DoesNotExist as e:
            raise Http404()

        return super(UserAdvertsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserAdvertsView, self).get_context_data(**kwargs)

        context['user_obj'] = self._user
        context['user_adverts_count'] = Advert.published_objects.filter(author=self._user).count()

        social_network = self.request.GET.get('social_network', '')

        if social_network:
            context['selected_social_network'] = social_network

        return context

    def get_queryset(self):
        qs = super(UserAdvertsView, self).get_queryset().filter(author=self._user)

        social_network = self.request.GET.get('social_network', '')

        if social_network:
            qs = qs.filter(social_account__social_network__code=social_network)

        return qs


class SocialNetworkView(AdvertFilterMixin, ListView):
    template_name = 'advert/social_network.html'
    ajax_items_template_name = 'advert/parts/advert_list.html'
    context_object_name = 'adverts'
    model = Advert
    paginate_by = 30

    def get_queryset(self):
        return super(SocialNetworkView, self).get_queryset().filter(
            social_account__social_network=self._social_network)


class NotFound(TemplateView):
    template_name = 'base/404.html'

    def render_to_response(self, context, *args, **kwargs):
        response = super(NotFound, self).render_to_response(context, **kwargs)
        response.status_code = 404

        return response

    def get_context_data(self, **kwargs):
        context = super(NotFound, self).get_context_data()

        context.update(recommended_adverts(context, order_by='-social_account__subscribers'))

        return context


page_not_found = NotFound.as_view()


"""
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
"""
