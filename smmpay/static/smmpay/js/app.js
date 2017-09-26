(function ($) {
    $(document).ready(function(e) {
       var process_in_progress = 0;

        // Filter form handlers
        if ($('#filter-form').length) {
            $('.header__filter').on('click', function (e) {
                e.stopPropagation();
                $('.filter').addClass('visible');
            });

            $('.filter').on('click', function (e) {
                e.stopPropagation();
            });

            $('.wrapper').on('click', function () {
                $('.filter').removeClass('visible');
            });

            jcf.setOptions('Select', {
                wrapNative: false,
                flipDropToFit: false,
                maxVisibleItems: 5
            });

            jcf.replaceAll();

            $('.filter__reset').on('click', function () {
                $('#filter-form input').val('');

                $('#filter-form select').each(function(k, v) {
                    $('option:first', this).prop('selected', true)
                });

                jcf.replaceAll();

                var url = new URI(window.location.href);

                $.each($('#filter-form').serializeArray(), function(index, item) {
                    if (url.hasQuery(item.name)) {
                        url.query('');

                        load_data(url, {});

                        return false;
                    }
                });
            });

            $('#filter-form').on('submit', function (e) {
                e.preventDefault();

                if (process_in_progress) {
                    return false;
                }

                var url = new URI(window.location.href);

                url.query('');

                $.each($('#filter-form').serializeArray(), function(index, item) {
                    if (item.value) {
                        url.addQuery(item.name, item.value);
                    }
                });

                load_data(url, {});
            });

            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url);
            });

            $('.filter__value').keydown(function (e) {
                if (e.keyCode == 46 || e.keyCode == 8 || e.keyCode == 9 || e.keyCode == 27 || e.keyCode == 65 && e.ctrlKey === true || e.keyCode >= 35 && e.keyCode <= 39) {
                    return;
                } else {
                    if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
                        e.preventDefault();
                    }
                }
            });
        }

        // Advert add form handlers
        if ($('#advert-add-form').length) {
            var advert_add_form = $('#advert-add-form');

            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                }
            });

            jcf.setOptions('Select', {
                wrapNative: false,
                flipDropToFit: false,
                maxVisibleItems: 5
            });

            jcf.replaceAll();

            $('.addition-title').on('click' , function() {
                $(this).toggleClass('active');
                $('.addition-box').slideToggle();
            });

            var link = '',
                link_check_progress = 0;

            $('input[name="link"]', advert_add_form).on('focusout', function(e) {
                var field = $(this),
                    wrapper = field.parent(),
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g,
                    info_table = $('.product-table_info');

                if (link == $.trim(field.val()) || link_check_progress) {
                    return false;
                }

                link = $.trim($(this).val());

                $('.error_input', wrapper).remove();

                info_table.empty();
                info_table.addClass('hidden');

                $('.hidden-field input', advert_add_form).val('');
                $('input[name="logo"]', advert_add_form).val('');

                $('.hidden-field', advert_add_form).addClass('hidden');

                if (!link) {
                    wrapper.append('<div class="error_input">' + gettext('This field is required') + '</div>');

                    return false;
                }else if (!link_pat.test(link)) {
                    wrapper.append('<div class="error_input">' + gettext('You have inserted an incorrect value for the link to the page, group or account that you are selling *') + '</div>');

                    return false;
                }

                link_check_progress = 1;

                $.get(advert_add_form.data('validation-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        $.each(response['fields'], function(field, value) {
                            var form_field = $('input[name="' + field + '"]', advert_add_form);

                            if (value) {
                                $(form_field).val(value);
                            } else {
                                $(form_field).parent().removeClass('hidden');
                            }
                        });

                        var info_table_html = '';

                        if (response['fields']['title']) {
                            info_table_html += '<li><span class="th">' + gettext('title') + '</span><span class="td">' + response['fields']['title'] + '</span></li>';
                        }

                        if (response['fields']['subscribers']) {
                            info_table_html += '<li><span class="th">' + gettext('subscribers') + '</span><span class="td">' + response['fields']['subscribers'] + '</span></li>';
                        }

                        if (info_table_html) {
                            info_table.append(info_table_html);
                            info_table.removeClass('hidden');
                        }
                    } else {
                        $('.item.hidden', advert_add_form).removeClass('hidden');
                    }

                    link_check_progress = 0;
                }, 'json');
            });

            advert_add_form.submit(function(e) {
                var error = 0,
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                $('.error_input', advert_add_form).remove();

                if (!$('input[name="link"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="link"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                } else if (!link_pat.test($('input[name="link"]', advert_add_form).val())) {
                    error = 1;

                    $('input[name="link"]', advert_add_form).after('<div class="error_input">' + gettext('You have inserted an incorrect value for the link to the page, group or account that you are selling *') + '</div>');
                }

                if (!$('select[name="category"]', advert_add_form).val()) {
                    error = 1;

                    $('select[name="category"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('select[name="region"]', advert_add_form).val()) {
                    error = 1;

                    $('select[name="region"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="price"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="price"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (error) {
                    e.preventDefault();
                }
            });
        }

        // Advert edit form handlers
        if ($('#advert-edit-form').length) {
            var advert_edit_form = $('#advert-edit-form');

            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                }
            });

            jcf.setOptions('Select', {
                wrapNative: false,
                flipDropToFit: false,
                maxVisibleItems: 5
            });

            jcf.replaceAll();

            $('.addition-title').on('click' , function() {
                $(this).toggleClass('active');
                $('.addition-box').slideToggle();
            });

            var link = '',
                link_check_progress = 0;

            $('input[name="link"]', advert_edit_form).on('focusout', function(e) {
                var field = $(this),
                    wrapper = field.parent(),
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                if (link == $.trim(field.val()) || link_check_progress) {
                    return false;
                }

                link = $.trim($(this).val());

                $('.error_input', wrapper).remove();

                if (!link) {
                    wrapper.append('<div class="error_input">' + gettext('This field is required') + '</div>');

                    return false;
                }else if (!link_pat.test(link)) {
                    wrapper.append('<div class="error_input">' + gettext('You have inserted an incorrect value for the link to the page, group or account that you are selling *') + '</div>');

                    return false;
                }

                link_check_progress = 1;

                $.get(advert_add_form.data('validation-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        $.each(response['fields'], function(field, value) {
                            var form_field = $('input[name="' + field + '"]', advert_add_form);

                            if (value) {
                                $(form_field).val(value);
                            }
                        });
                    }

                    link_check_progress = 0;
                }, 'json');
            });

            advert_edit_form.submit(function(e) {
                var error = 0,
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                $('.error_input', advert_add_form).remove();

                if (!$('input[name="link"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="link"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                } else if (!link_pat.test($('input[name="link"]', advert_add_form).val())) {
                    error = 1;

                    $('input[name="link"]', advert_add_form).after('<div class="error_input">' + gettext('You have inserted an incorrect value for the link to the page, group or account that you are selling *') + '</div>');
                }

                if (!$('select[name="category"]', advert_add_form).val()) {
                    error = 1;

                    $('select[name="category"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('select[name="region"]', advert_add_form).val()) {
                    error = 1;

                    $('select[name="region"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="price"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="price"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (error) {
                    e.preventDefault();
                }
            });
        }

        // Login form handlers
        if ($('#login-form').length) {
            $('#login-form').submit(function(e) {
                var form = $(this),
                    email_pat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
                    error = 0;

                $('.error_input', form).remove();

                if (!$('input[name="username"]', form).val()) {
                    error = 1;

                    $('input[name="username"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }else if (!email_pat.test($('input[name="username"]', form).val())) {
                    error = 1;

                    $('input[name="username"]', form).after('<div class="error_input">' + gettext('Incorrect email address') + '</div>');
                }

                if (!$('input[name="password"]', form).val()) {
                    error = 1;

                    $('input[name="password"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (error) {
                    e.preventDefault();
                }
            });
        }

        // Registration form handlers
        if ($('#registration-form').length) {
            $('#registration-form').submit(function(e) {
                var form = $(this),
                    email_pat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
                    error = 0;

                $('.error_input', form).remove();

                if (!$('input[name="first_name"]', form).val()) {
                    error = 1;

                    $('input[name="first_name"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="email"]', form).val()) {
                    error = 1;

                    $('input[name="email"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }else if (!email_pat.test($('input[name="email"]', form).val())) {
                    error = 1;

                    $('input[name="email"]', form).after('<div class="error_input">' + gettext('Incorrect email address') + '</div>');
                }

                if (!$('input[name="password1"]', form).val()) {
                    error = 1;

                    $('input[name="password1"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="password2"]', form).val()) {
                    error = 1;

                    $('input[name="password2"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (error) {
                    e.preventDefault();
                }
            });
        }

        // Password reset form handlers
        if ($('#password-reset-form').length) {
            $('#password-reset-form').submit(function(e) {
                var form = $(this),
                    email_pat = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
                    error = 0;

                $('.error_input', form).remove();

                if (!$('input[name="email"]', form).val()) {
                    error = 1;

                    $('input[name="email"]', form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }else if (!email_pat.test($('input[name="email"]', form).val())) {
                    error = 1;

                    $('input[name="email"]', form).after('<div class="error_input">' + gettext('Incorrect email address') + '</div>');
                }

                if (error) {
                    e.preventDefault();
                }
            });
        }

        // Advert view page handlers
        if ($('.inner-product').length) {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                }
            });

            var views_counter = $('.thumb__view a');

            setTimeout(function() {
                $.get(views_counter.data('views-url'), {}, function(response) {
                    if (response['success']) {
                        var current_views = parseInt($('i', views_counter).text().match(/(\d+)/)) + 1;

                        $('i', views_counter).text('(' + current_views + ')');
                    }
                }, 'json');
            }, 5000);

            $('#advert-message-form').submit(function(e) {
               e.preventDefault();

               var message_form = $(this);

               $('.error', message_form).removeClass('error');

               if (!$.trim($('textarea[name="message"]', message_form).val())) {
                   $('textarea[name="message"]', message_form).addClass('error');

                   return false;
               }

               $.post(message_form.attr('action'), message_form.serialize(), function(response) {
                   if(response['success']) {
                       message_form.trigger('reset');

                       $('textarea[name="message"]', message_form).after('<div class="message">' + gettext('Your message was successfully sent') + '</div>');

                       setTimeout(function() {
                           $('.message', message_form).remove();
                       }, 5000);
                   } else if (response['errors']) {
                       $.each(response['errors'], function (k, v) {
                            $('[name="' + k + '"]', message_form).addClass('error');
                        });
                   }
               }, 'json');
            });
        }

        // Account setting page
        if ($('.sidebar-user_cabinet').length) {
            jcf.replaceAll();
        }

        // Account search form handlers
        if ($('#account-search-form').length) {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                }
            });

            jcf.setOptions('Select', {
                wrapNative: false,
                flipDropToFit: false,
                maxVisibleItems: 5
            });

            jcf.replaceAll();

            $('#account-search-form').submit(function(e) {
                e.preventDefault();

                var form = $(this),
                    url = new URI(window.location.href);

                url.query('');

                $.each(form.serializeArray(), function(index, item) {
                    if (item.value) {
                        url.addQuery(item.name, item.value);
                    }
                });

                load_data(url, {}, $('.items'));
            });

            $('#account-search-form select[name="order"]').change(function(e) {
                $('#account-search-form').submit();
            });
        }

        // Account adverts page handlers
        if ($('.user-ads_content').length) {
            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url, {}, $('.items'));
            });
        }

        // Account discussions page handlers
        if ($('.user-mail_content').length) {
            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url, {}, $('.items'));
            });
        }

        // Account discussion page handlers
        if ($('.user-dialog_content').length) {
            var chat = $('.scroll-chat'),
                discussion_page = 2,
                last_page = false;

            chat.animate({scrollTop: chat.height()}, 0, 'swing', function() {
                if (chat.attr('data-has-next-page') !== 'False') {
                    chat.bind('scroll', function (e) {
                        if (!last_page && $(this).scrollTop() <= 0) {
                            var first_item = $('.item:first', chat);

                            $.get(window.location.pathname, {page: discussion_page}, function(response) {
                                if (response['success']) {
                                    chat.prepend(response['data']);

                                    jcf.refreshAll();

                                    chat.scrollTop(first_item.position().top);

                                    if (response['has_next_page']) {
                                        discussion_page += 1;
                                    } else {
                                        last_page = true;
                                    }
                                }
                            }, 'json');
                        }

                        add_views(chat);
                    });
                }
            });

            $('#discussion-message-form').submit(function(e) {
                var message_form = $(this);

               $('.error', message_form).removeClass('error');

               if (!$.trim($('textarea[name="message"]', message_form).val())) {
                   $('textarea[name="message"]', message_form).addClass('error');

                   e.preventDefault();
               }
            });

            function add_views(chat) {
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    }
                });

                var chat_height = chat.height(),
                    chat_top = chat.scrollTop(),
                    chat_bottom = chat_top + chat_height,
                    new_messages_counter = $('.nav-advertise .number'),
                    messages = [];

                $('.new-message:not(.checking)', chat).each(function() {
                    var elem_top = $(this).offset().top - chat.offset().top;
                    var elem_bottom = elem_top + $(this).height();

                    if (elem_top >= 0 && elem_bottom <= chat_height) {
                        $(this).addClass('checking');

                        messages.push($(this));
                    }
                });

                if (messages.length) {
                    var messages_ids = messages.map(function(item) {
                        return item.data('id');
                    });

                    $.post(chat.data('views-url'), {messages_ids: messages_ids}, function(response){
                        if (response['success']) {
                            setTimeout(function() {
                                $.each(messages, function() {
                                    $(this).removeClass('new-message').removeClass('checking');
                                });

                                var messages_count = parseInt(new_messages_counter.text());
                                new_messages_counter.text(messages_count - messages_ids.length);
                            }, 5000);
                        }
                    }, 'json');
                }
            };
        }

        // Account favorites page handlers
        if ($('.user-favorites_content').length) {
            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url, {}, $('.items'));
            });
        }

        // Blog handlers
        if ($('.content-blog').length) {
            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url, {});
            });
        }

        // General
        $('.model-window,.popup .close-btn').on('click' , function(e) {
            e.stopPropagation();
            $('.model-window').fadeOut(200);
        });

        $('.popup-hint-info,.popup-user_message').on('click', function(e) {
            e.stopPropagation();
        });

        $('.btn-write').on('click', function(e) {
            $('#model-user_message').fadeIn(200);
        });

        $('.hint-info_box .close-btn').on('click' , function() {
            $(this).parent().removeClass('show');
        });


        function load_data(url, data, element) {
            var content = typeof element != 'undefined' ? element : $('.inner__content');

            preloader_show();

            window.history.pushState('', '', url);

            $.get(url, data, function(response) {
                if (response['success']) {
                    content.empty().append(response['data']);

                    $('html, body').animate({scrollTop: 0});
                }

                preloader_hide();
            }, 'json');
        }

        function preloader_show() {
            $('.preloader-content').show();

            process_in_progress = 1;
        }

        function preloader_hide() {
            $('.preloader-content').hide();

            process_in_progress = 0;
        }

        function getCookie(name) {
            var cookieValue = null;

            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');

                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);

                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }

            return cookieValue;
        }

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
    });
}(jQuery));