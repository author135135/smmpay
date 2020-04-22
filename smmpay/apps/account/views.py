# import json

from django.http import Http404, JsonResponse
from django.views.generic import TemplateView, RedirectView, ListView, DeleteView, View
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse, reverse_lazy
# from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q, Case, Sum, When, IntegerField
from django.utils.translation import gettext_lazy as _

# from registration.backends.hmac import views
# from channels import Group
from django_registration.backends.activation import views
# from smmpay.apps.advert.models import Discussion, DiscussionUser, Advert, FavoriteAdvert
from smmpay.apps.advert.models import Advert, FavoriteAdvert, SocialNetwork

# from .forms import RegistrationForm, ProfileForm, PasswordChangeForm, EmailChangeForm, DiscussionMessageForm,
# SearchForm
from .forms import RegistrationForm, ProfileForm, PasswordChangeForm, EmailChangeForm, SearchForm
from .models import Profile
from .tokens import email_change_token_generator


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class SearchMixin(object):
    def get_queryset(self):
        qs = super(SearchMixin, self).get_queryset()

        filter_form = self._get_search_form()
        form_data = filter_form.initial

        if filter_form.is_valid():
            form_data.update({k: v for k, v in filter_form.cleaned_data.items() if v})

        for item in self.filters:
            if not filter_form.has_error(item) and item in form_data:
                search_value = form_data[item]
                qs_query = None

                for expression in self.filters[item]:
                    if qs_query is None:
                        qs_query = Q(**{expression: search_value})
                    else:
                        qs_query |= Q(**{expression: search_value})

                if qs_query is not None:
                    qs = qs.filter(qs_query)

        sort_by_value = form_data.get('sort_by', None)

        if sort_by_value:
            sort_by = sort_by_value

        qs = qs.order_by(sort_by)

        print(qs.query)

        return qs

    def get_context_data(self, **kwargs):
        context = super(SearchMixin, self).get_context_data(**kwargs)
        context['search_form'] = self._get_search_form()

        return context

    def _get_search_form(self):
        if not hasattr(self, 'search_form'):
            social_network_choices = self.get_social_network_choices()
            sort_choices = self.SORT_CHOICES

            initial = {
                'social_network': '',
                'sort_by': sort_choices[0][0]
            }

            if social_network_choices:
                initial['social_network'] = social_network_choices[0][0]

            self.search_form = SearchForm(data=self.request.GET or None, social_network_choices=social_network_choices,
                                          sort_choices=sort_choices, initial=initial)

        return self.search_form


class IndexView(LoginRequiredMixin, SearchMixin, ListView):
    template_name = 'account/index.html'
    ajax_template_name = 'account/parts/advert_list.html'
    model = Advert
    context_object_name = 'adverts'
    paginate_by = 4

    filters = {
        'search_query': ['title__icontains', 'description__icontains'],
        'social_network': ['social_account__social_network__code']
    }

    SORT_CHOICES = (
        ('created', {'label': _('Latest'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-created', {'label': _('Latest'), 'data-imagesrc': static('smmpay/images/sort_higher.png')}),
        ('min_price', {'label': _('price min'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-min_price', {'label': _('price min'), 'data-imagesrc': static('smmpay/images/sort_higher.png')}),
        ('max_price', {'label': _('price max'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-max_price', {'label': _('price max'), 'data-imagesrc': static('smmpay/images/sort_higher.png')})
    )

    def get(self, request, *args, **kwargs):
        response = super(IndexView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            return JsonResponse({
                'success': True,
                'data': render_to_string(self.ajax_template_name, response.context_data, request)
            })

        return response

    def get_queryset(self):
        qs = super(IndexView, self).get_queryset()
        qs &= self.model.objects.get_extra_queryset(select_items=['advert_in_favorite_count']).filter(
            author=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['adverts_count'] = context['paginator'].count
        context['advert_statuses'] = {
            'ADVERT_STATUS_MODERATION': Advert.ADVERT_STATUS_MODERATION,
            'ADVERT_STATUS_VIOLATION': Advert.ADVERT_STATUS_VIOLATION,
        }

        return context

    def get_social_network_choices(self):
        social_network_choices = []

        social_network_qs = SocialNetwork.objects.annotate(adverts_count=Sum(
            Case(
                When(Q(social_accounts__advert__author=self.request.user), then=1),
                default=0, output_field=IntegerField()
            )
        ))

        for social_network in social_network_qs:
            social_network_choices.append((
                social_network.code,
                {'label': '{} ({})'.format(social_network.title, social_network.adverts_count),
                 'data-imagesrc': static('smmpay/images/{}_icon.svg'.format(social_network.code))}
            ))
        return social_network_choices


class FavoritesView(LoginRequiredMixin, SearchMixin, ListView):
    template_name = 'account/favorites.html'
    ajax_template_name = 'account/parts/favorite_list.html'
    model = FavoriteAdvert
    context_object_name = 'favorites'
    paginate_by = 4

    filters = {
        'search_query': ['advert__title__icontains', 'advert__description__icontains'],
        'social_network': ['advert__social_account__social_network__code']
    }

    SORT_CHOICES = (
        ('advert__created', {'label': _('Latest'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-advert__created', {'label': _('Latest'), 'data-imagesrc': static('smmpay/images/sort_higher.png')}),
        ('advert__min_price', {'label': _('price min'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-advert__min_price', {'label': _('price min'), 'data-imagesrc': static('smmpay/images/sort_higher.png')}),
        ('advert__max_price', {'label': _('price max'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-advert__max_price', {'label': _('price max'), 'data-imagesrc': static('smmpay/images/sort_higher.png')})
    )

    def get(self, request, *args, **kwargs):
        response = super(FavoritesView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            return JsonResponse({
                'success': True,
                'data': render_to_string(self.ajax_template_name, response.context_data, request)
            })

        return response

    def get_queryset(self):
        return super(FavoritesView, self).get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(FavoritesView, self).get_context_data(**kwargs)

        context['adverts_count'] = context['paginator'].count

        return context

    def get_social_network_choices(self):
        social_network_choices = []
        favorite_adverts = FavoriteAdvert.objects.filter(user=self.request.user).values_list('advert', flat=True)

        social_network_qs = SocialNetwork.objects.annotate(adverts_count=Sum(
            Case(
                When(Q(social_accounts__advert__in=favorite_adverts), then=1),
                default=0, output_field=IntegerField()
            )
        ))

        for social_network in social_network_qs:
            social_network_choices.append((
                social_network.code,
                {'label': '{} ({})'.format(social_network.title, social_network.adverts_count),
                 'data-imagesrc': static('smmpay/images/{}_icon.svg'.format(social_network.code))}
            ))
        return social_network_choices


"""
class DiscussionsView(LoginRequiredMixin, SearchMixin, ListView):
    template_name = 'account/discussions.html'
    ajax_template_name = 'account/parts/discussion_list.html'
    model = Discussion
    context_object_name = 'discussions'
    paginate_by = 4

    search_fields = ('advert__title', 'advert__description')
    sorting_fields = ('advert__price', 'created')

    SORT_CHOICES = (
        ('created_desc', _('Newer first')),
        ('created_asc', _('Older first')),
        ('advert__price_desc', _('Highest price')),
        ('advert__price_asc', _('Lowest price')),
    )

    def get(self, request, *args, **kwargs):
        response = super(DiscussionsView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            return JsonResponse({
                'success': True,
                'data': render_to_string(self.ajax_template_name, response.context_data, request)
            })

        return response

    def get_queryset(self):
        qs = super(DiscussionsView, self).get_queryset()
        qs &= self.model.objects.get_extra_queryset(select_items=['new_messages_count']).filter(users=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        context = super(DiscussionsView, self).get_context_data(**kwargs)

        context['search_form'] = SearchForm(data=self.request.GET or None,
                                            order_choices=self.SORT_CHOICES,
                                            initial={'order': 'created_desc'})

        return context


class DiscussionView(LoginRequiredMixin, DetailView):
    template_name = 'account/discussion.html'
    context_object_name = 'discussion'
    ajax_template_name = 'account/parts/discussion_message_list.html'
    paginate_by = 4

    def get(self, request, *args, **kwargs):
        response = super(DiscussionView, self).get(request, *args, **kwargs)

        if request.is_ajax():
            return JsonResponse({
                'success': True,
                'data': render_to_string(self.ajax_template_name, response.context_data, request),
                'has_next_page': response.context_data['has_next_page']
            })

        return response

    def get_context_data(self, **kwargs):
        context = super(DiscussionView, self).get_context_data(**kwargs)

        discussion_user = DiscussionUser.objects.get(discussion=self.object, user=self.request.user)

        messages_qs = self.object.discussion_messages.get_extra_queryset(select_items=['is_viewed'],
                                                                         select_params=[discussion_user.pk])
        messages_qs = messages_qs.select_related('sender__user__profile').reverse()

        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(messages_qs, self.paginate_by)

        if paginator.num_pages < page:
            raise Http404()

        page_obj = paginator.page(self.request.GET.get('page', 1))

        context['discussion_messages'] = reversed(page_obj.object_list)
        context['has_next_page'] = page_obj.has_next()
        context['form'] = DiscussionMessageForm

        context['advert_statuses'] = {
            'ADVERT_STATUS_MODERATION': Advert.ADVERT_STATUS_MODERATION,
            'ADVERT_STATUS_VIOLATION': Advert.ADVERT_STATUS_VIOLATION,
        }

        return context

    def get_object(self):
        try:
            discussion = Discussion.objects.get_extra_queryset(select_items=['new_messages_count']).get(
                users=self.request.user, pk=self.kwargs['pk'])
        except Discussion.DoesNotExist:
            raise Http404()

        return discussion


class DiscussionMessageAddView(FormView):
    message_sender_template_name = 'account/parts/discussion_message_sender.html'
    message_recipient_template_name = 'account/parts/discussion_message_recipient.html'
    form_class = DiscussionMessageForm

    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(['post'])

    def form_valid(self, form):
        response = {
            'success': False
        }

        if self.request.user.is_authenticated():
            try:
                discussion = Discussion.objects.get(pk=self.kwargs['pk'], users=self.request.user)
                discussion_message = discussion.add_message(self.request.user, form.cleaned_data['message'])

                context_data = {
                    'discussion_message': discussion_message
                }

                response['success'] = True
                response['data'] = render_to_string(self.message_sender_template_name, context_data, self.request)

                group_keyword = 'discussion-{}'.format(self.kwargs['pk'])
                group = Group(group_keyword)

                group.send({
                    'text': json.dumps({
                        'sender': self.request.user.pk,
                        'data': render_to_string(self.message_recipient_template_name, context_data, self.request)
                    })
                })
            except Discussion.DoesNotExist:
                pass

        return JsonResponse(response)

    def form_invalid(self, form):
        response = {
            'success': False,
            'errors': form.errors
        }

        return JsonResponse(response)


class DiscussionMessageViewAddView(View):
    def post(self, *args, **kwargs):
        response_data = {
            'success': False
        }

        if self.request.user.is_authenticated():
            messages_ids = self.request.POST.getlist('messages_ids[]')

            try:
                discussion = Discussion.objects.get(pk=kwargs['pk'], users=self.request.user)

                discussion_user = discussion.discussion_users.get(user=self.request.user)

                discussion_messages = discussion.discussion_messages.filter(pk__in=messages_ids).exclude(
                    sender=discussion_user)

                for message in discussion_messages:
                    message.mark_as_viewed(discussion_user)

                response_data['success'] = True
            except Discussion.DoesNotExist:
                pass

        return JsonResponse(response_data)
"""


class FavoriteDeleteView(View):
    def post(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            favorite_id = request.POST.get('favorite_id', None)

            if favorite_id is not None:
                try:
                    favorite = FavoriteAdvert.objects.get(pk=favorite_id, user=request.user)
                    favorite.delete()

                    response_data['success'] = True
                except FavoriteAdvert.DoesNotExist:
                    pass

        return JsonResponse(response_data)


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'account/settings.html'

    forms = {
        'profile_form': ProfileForm,
        'password_change_form': PasswordChangeForm,
        'email_change_form': EmailChangeForm
    }

    success_messages = {
        'profile_form': _('Profile data updated'),
        'password_change_form': _('Your password has been successfully changed'),
        'email_change_form': _('Mail with instructions was sent on your current email address'),
    }

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)

        form_type = self._get_form_type()
        forms = self._get_forms()

        if form_type in kwargs:
            forms[form_type] = kwargs[form_type]

        context.update(forms)

        return context

    def post(self, request, *args, **kwargs):
        form_type = self._get_form_type()

        form = self._get_forms().get(form_type, None)

        if form is None:
            raise Http404

        if form.is_valid():
            form.save(request=request)

            messages.add_message(request, messages.SUCCESS, self._get_success_message(form_type))

            return redirect(reverse('account:settings'))

        return self.render_to_response(self.get_context_data(**{form_type: form}))

    def _get_form_type(self):
        return self.request.POST.get('form_type', None)

    def _get_forms(self):
        forms_dict = {}

        for form_type, form_class in self.forms.items():
            form_kwargs = {}

            form_kwargs_method = '_get_kwargs_%s' % form_type

            if form_type == self._get_form_type():
                form_kwargs['data'] = self.request.POST

            if hasattr(self, form_kwargs_method):
                form_kwargs.update(getattr(self, form_kwargs_method)())
            forms_dict[form_type] = form_class(**form_kwargs)

        return forms_dict

    def _get_kwargs_profile_form(self):
        kwargs = {
            'user': self.request.user,
            'initial': {
                'first_name': self.request.user.profile.first_name,
                'phone_number': self.request.user.profile.phone_number,
                'is_profile_public': self.request.user.is_profile_public,
            }
        }

        return kwargs

    def _get_kwargs_password_change_form(self):
        return {'user': self.request.user}

    def _get_kwargs_email_change_form(self):
        return {'request': self.request}

    def _get_success_message(self, form_type):
        return self.success_messages.get(form_type, None)


class RegistrationView(views.RegistrationView):
    form_class = RegistrationForm

    def dispatch(self, *args, **kwargs):
        dispatch = super(RegistrationView, self).dispatch(*args, **kwargs)

        if self.request.user.is_authenticated():
            return redirect(reverse('advert:index'))

        return dispatch

    def get_success_url(self, user):
        return reverse('account:django_registration_complete')

    def register(self, form):
        new_user = super(RegistrationView, self).register(form)

        # Set Profile model fields if presented in form
        profile_fields = [model_field.name for model_field in Profile._meta.get_fields()]

        for field in form.cleaned_data:
            if field in profile_fields:
                setattr(new_user.profile, field, form.cleaned_data.get(field))

        new_user.save()

        return new_user


class ActivationView(views.ActivationView):
    def get_success_url(self, user):
        return reverse('account:account_activation_complete')


class ActivationCompleteView(TemplateView):
    template_name = 'django_registration/activation_complete.html'


class EmailChangeConfirmView(LoginRequiredMixin, RedirectView):
    permanent = False
    url = reverse_lazy('account:settings')

    def get(self, request, *args, **kwargs):
        user = request.user

        token = kwargs['token']

        if email_change_token_generator.check_token(user, token):
            email_token_obj = email_change_token_generator.get_token(user, token)

            user.email = email_token_obj.email
            user.save()

            email_token_obj.delete()
        else:
            raise Http404

        return super(EmailChangeConfirmView, self).get(self, request, *args, **kwargs)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'account/account_delete.html'
    success_url = reverse_lazy('account:login')

    def get_object(self, queryset=None):
        return self.request.user


class AdvertChangeStatusView(View):
    def post(self, request, *args, **kwargs):
        response_data = {
            'success': False
        }

        if request.user.is_authenticated():
            advert_id = request.POST.get('advert_id', None)

            if advert_id is not None:
                try:
                    advert = Advert.objects.get(pk=advert_id, author=request.user)
                    advert.enabled_by_author = int(not advert.enabled_by_author)
                    advert.save()

                    response_data = {
                        'success': True,
                        'status': advert.enabled_by_author
                    }
                except Advert.DoesNotExist:
                    pass

        return JsonResponse(response_data)
