import json

from django.http import Http404, JsonResponse, HttpResponseNotAllowed
from django.views.generic import TemplateView, RedirectView, ListView, DeleteView, FormView, DetailView, View
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from registration.backends.hmac import views
from channels import Group
from smmpay.apps.advert.models import Discussion, DiscussionUser, Advert, FavoriteAdvert

from .forms import RegistrationForm, ProfileForm, PasswordChangeForm, EmailChangeForm, DiscussionMessageForm, SearchForm
from .models import Profile
from .tokens import email_change_token_generator


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdvertChangeStatusMixin(object):
    model = Advert
    advert_status = True

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(pk=self.kwargs['pk'], author=self.request.user,
                                          enabled_by_author=not self.advert_status)
        except self.model.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        advert = self.get_object()

        advert.enabled_by_author = self.advert_status
        advert.save()

        return redirect(self.request.GET.get('next', reverse('account:index')))


class SearchMixin(object):
    def get_queryset(self):
        qs = super(SearchMixin, self).get_queryset()

        order = self.request.GET.get('order', 'created_desc')

        try:
            order_field, order_type = order.rsplit('_', 1)

            if order_field in self.sorting_fields:
                order_str = ''
                order_type = order_type.lower()

                if order_type == 'desc':
                    order_str = '-{}'
                else:
                    order_str = '{}'

                qs = qs.order_by(order_str.format(order_field))
        except ValueError:
            pass

        query = self.request.GET.get('query', '')
        query = query.strip()

        if query:
            qs_query = None

            for field in self.search_fields:
                if qs_query is None:
                    qs_query = Q(**{'{}__icontains'.format(field): query})
                else:
                    qs_query |= Q(**{'{}__icontains'.format(field): query})

            qs = qs.filter(qs_query)

        return qs


class IndexView(LoginRequiredMixin, SearchMixin, ListView):
    template_name = 'account/index.html'
    ajax_template_name = 'account/parts/advert_list.html'
    model = Advert
    context_object_name = 'adverts'
    paginate_by = 4

    search_fields = ('title', 'description')
    sorting_fields = ('price', 'created')

    SORT_CHOICES = (
        ('created_desc', _('Newer first')),
        ('created_asc', _('Older first')),
        ('price_desc', _('Highest price')),
        ('price_asc', _('Lowest price')),
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
        qs = super(IndexView, self).get_queryset().select_related('social_account')
        qs &= self.model.objects.get_extra_queryset(select_items=['new_messages_count']).filter(
            author=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['search_form'] = SearchForm(data=self.request.GET or None,
                                            order_choices=self.SORT_CHOICES,
                                            initial={'order': 'created_desc'})

        return context


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
    def get(self, *args, **kwargs):
        return HttpResponseNotAllowed(['post'])

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


class FavoritesView(LoginRequiredMixin, SearchMixin, ListView):
    template_name = 'account/favorites.html'
    ajax_template_name = 'account/parts/favorite_list.html'
    model = FavoriteAdvert
    context_object_name = 'favorites'
    paginate_by = 4

    search_fields = ('advert__title', 'advert__description')
    sorting_fields = ('advert__price', 'advert__created')

    SORT_CHOICES = (
        ('advert__created_desc', _('Newer first')),
        ('advert__created_asc', _('Older first')),
        ('advert__price_desc', _('Highest price')),
        ('advert__price_asc', _('Lowest price')),
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

        context['search_form'] = SearchForm(data=self.request.GET or None,
                                            order_choices=self.SORT_CHOICES,
                                            initial={'order': 'created_desc'})

        return context


class FavoriteDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            favorite = FavoriteAdvert.objects.get(pk=kwargs['pk'])
            favorite.delete()
        except FavoriteAdvert.DoesNotExist:
            raise Http404

        return redirect(request.GET.get('next', reverse('account:favorites')))


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
    template_name = 'registration/registration.html'
    form_class = RegistrationForm

    def get_success_url(self, user):
        return reverse('account:registration_complete')

    def register(self, form):
        new_user = super(RegistrationView, self).register(form)

        # Set Profile model fields if presented in form
        profile_fields = Profile._meta.get_fields()

        for field in form.cleaned_data:
            if field in profile_fields:
                setattr(new_user.profile, field, form.cleaned_data.get(field))

        new_user.save()

        return new_user


class ActivationView(views.ActivationView):
    def get_success_url(self, user):
        return reverse('account:registration_activation_complete')


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


class AdvertDeactivateView(LoginRequiredMixin, AdvertChangeStatusMixin, DetailView):
    advert_status = False


class AdvertActivateView(LoginRequiredMixin, AdvertChangeStatusMixin, DetailView):
    advert_status = True
