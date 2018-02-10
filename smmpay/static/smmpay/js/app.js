(function ($) {
    $(document).ready(function(e) {
        var process_in_progress = 0;

        $.ajaxSetup({
            cache: false
        });

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
                var need_reload = false;

                $('#filter-form input').val('');

                $('#filter-form select').each(function(k, v) {
                    $('option:first', this).prop('selected', true)
                });

                jcf.replaceAll();

                var url = new URI(window.location.href);

                url.removeQuery('page');

                $.each($('#filter-form').serializeArray(), function(index, item) {
                    if (url.hasSearch(item.name)) {
                        url.removeQuery(item.name);
                        need_reload = true;
                    }
                });

                $('.filter__form-social a').each(function() {
                    var link_url = new URI($(this).attr('href')),
                        link_url_query = link_url.query(true);

                    delete link_url_query['page'];

                    for (var key in link_url_query) {
                        if (key !== 'social_network') {
                            delete link_url_query[key];
                        }
                    }

                    link_url.query(link_url_query);

                    $(this).attr('href', link_url);
                });

                if (need_reload) {
                    load_data(url, {}, $('.items'));
                }
            });

            $('#filter-form').on('submit', function (e) {
                e.preventDefault();

                if (process_in_progress) {
                    return false;
                }

                var url = new URI(window.location.href),
                    url_query = url.query(true);

                delete url_query['page'];

                $.each($('#filter-form').serializeArray(), function(index, item) {
                    if (item.value) {
                        url_query[item.name] = item.value;
                    } else {
                        delete url_query[item.name];
                    }
                });

                url.query(url_query);

                $('.filter__form-social a').each(function() {
                    var link_url = new URI($(this).attr('href')),
                        link_url_query = link_url.query(true);

                    url_query['social_network'] = link_url_query['social_network'];

                    link_url.query(url_query);

                    $(this).attr('href', link_url);
                });

                load_data(url, {}, $('.items'));
            });

            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url, {}, $('.items'));
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

            $('.filter__form-social a').click(function(e) {
                e.preventDefault();

                if (process_in_progress) {
                    return false;
                }

                var url = new URI($(this).attr('href'));

                load_data(url, {}, $('.items'));

                $('.filter__form-social .active').removeClass('active');
                $(this).parent().addClass('active');
            })
        }

        // Add/delete favorites handlers
        if ($('.thumb__favorite').length) {
            $(document).on('click', '.thumb__favorite', function(e) {
                e.preventDefault();

                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    }
                });

                var link = $(this);

                if (is_user_authenticated()) {
                    $.post(link.data('favorite-url'), {'advert_id': link.data('item-id')}, function(response) {
                        if (response['success']) {
                            link.toggleClass('active ');
                            if (response['in_favorite']) {
                                $('span', link).text(gettext('Delete from favorites'));
                            } else {
                                $('span', link).text(gettext('Add to favorites'));
                            }
                        }
                    }, 'json');
                } else {
                    modal(gettext('You must be logged to perform this operation'));
                }
            })
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

            autosize($('textarea[name="description"]', advert_add_form));

            var link = $('input[name="link"]', advert_add_form).val() ? $('input[name="link"]', advert_add_form).val(): '',
                link_check_progress = 0;

            $('input[name="link"]', advert_add_form).on('focusout', function(e) {
                var field = $(this),
                    wrapper = field.parent(),
                    info_table = $('.product-table_info');

                if (link == $.trim(field.val()) || link_check_progress) {
                    return false;
                }

                link = $.trim($(this).val());

                $('.error_input', wrapper).remove();
                $('.hidden-field .error_input', advert_add_form).remove();

                info_table.empty();
                info_table.addClass('hidden');

                $('.hidden-field input', advert_add_form).val('');
                $('input[name="external_logo"]', advert_add_form).val('');

                $('.hidden-field', advert_add_form).addClass('hidden');

                var result = check_link(link);

                if (!result['success']) {
                    wrapper.append('<div class="error_input">' + result['error'] + '</div>');

                    return false;
                }

                link_check_progress = 1;

                preloader_show();

                $.get(advert_add_form.data('validation-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        $.each(response['fields'], function(field, value) {
                            var form_field = $('input[name="' + field + '"]', advert_add_form);

                            if (value) {
                                $(form_field).val(value);
                            } else {
                                if (field === 'external_logo') {
                                    form_field = $('input[name="logo"]', advert_add_form);
                                }

                                $(form_field).parent().removeClass('hidden');
                            }
                        });

                        var info_table_html = '';

                        if (response['fields']['external_logo']) {
                            info_table_html += '<li><span class="th">' + gettext('logo') + '</span><span class="td"><a class="thumb__avatar"><img src="' + response['fields']['external_logo'] + '"></a></span></li>';
                        }

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

                    preloader_hide();
                }, 'json');
            });

            advert_add_form.submit(function(e) {
                var error = 0,
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                $('.error_input', advert_add_form).remove();

                var result = check_link(link);

                if (!result['success']) {
                    $('input[name="link"]', advert_add_form).after('<div class="error_input">' + result['error'] + '</div>');

                    error = 1;
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

                    $('input[name="price"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && !$('input[name="title"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="title"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && !$('input[name="subscribers"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="subscribers"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && !$('input[name="external_logo"]', advert_add_form).val() && !$('input[name="logo"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="logo"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
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

            autosize($('textarea[name="description"]', advert_edit_form));

            var link = $('input[name="link"]', advert_edit_form).val() ? $('input[name="link"]', advert_edit_form).val(): '',
                link_check_progress = 0;

            $('input[name="link"]', advert_edit_form).on('focusout', function(e) {
                var field = $(this),
                    wrapper = field.parent(),
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g,
                    info_table = $('.product-table_info');

                if (link == $.trim(field.val()) || link_check_progress) {
                    return false;
                }

                link = $.trim($(this).val());

                $('.hidden-field .error_input', advert_add_form).remove();
                $('.error_input', wrapper).remove();

                $('.hidden-field input', advert_edit_form).val('');
                $('input[name="external_logo"]', advert_edit_form).val('');

                info_table.empty();

                var result = check_link(link);

                if (!result['success']) {
                    wrapper.append('<div class="error_input">' + result['error'] + '</div>');

                    return false;
                }

                link_check_progress = 1;

                preloader_show();

                $.get(advert_edit_form.data('validation-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        $.each(response['fields'], function(field, value) {
                            var form_field = $('input[name="' + field + '"]', advert_edit_form);

                            if (value) {
                                $(form_field).val(value);
                            }
                        });

                        if (response['fields']['external_logo']) {
                            info_table.append('<li><a class="thumb__avatar"><img src="' + response['fields']['external_logo'] + '"></a></li>');
                        }
                    }

                    link_check_progress = 0;

                    preloader_hide();
                }, 'json');
            });

            advert_edit_form.submit(function(e) {
                var error = 0,
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                $('.error_input', advert_edit_form).remove();

                var result = check_link(link);

                if (!result['success']) {
                    $('input[name="link"]', advert_edit_form).after('<div class="error_input">' + result['error'] + '</div>');

                    error = 1;
                }

                if (!$('select[name="category"]', advert_edit_form).val()) {
                    error = 1;

                    $('select[name="category"]', advert_edit_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('select[name="region"]', advert_edit_form).val()) {
                    error = 1;

                    $('select[name="region"]', advert_edit_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="price"]', advert_edit_form).val()) {
                    error = 1;

                    $('input[name="price"]', advert_edit_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="title"]', advert_edit_form).val()) {
                    error = 1;

                    $('input[name="title"]', advert_edit_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="subscribers"]', advert_edit_form).val()) {
                    error = 1;

                    $('input[name="subscribers"]', advert_edit_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
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

                        $('#model-user_message').fadeOut(200);

                        modal(gettext('Your message was successfully sent'));
                    } else if (response['errors']) {
                        $.each(response['errors'], function (k, v) {
                            $('[name="' + k + '"]', message_form).addClass('error');
                        });
                    }
                }, 'json');
            });
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

        // Advert activate/deactivate handlers
        if ($('.thumb__delete').length) {
            $(document).on('click', '.thumb__delete a', function(e) {
                e.preventDefault();

                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    }
                });

                var link = $(this),
                    wrapper = link.parent();

                $.post(link.data('change-status-url'), {'advert_id': link.data('item-id')}, function(response) {
                    if (response['success']) {
                        wrapper.toggleClass('deactivate-adt_btn active-adt_btn');

                        if (response['status']) {
                            $('span', wrapper).text(gettext('Active'));
                            link.text(gettext('Deactivate'));
                        } else {
                            $('span', wrapper).text(gettext('Deactivated'));
                            link.text(gettext('Activate'));
                        }
                    }
                }, 'json');
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
            jcf.replaceAll();

            var chat = $('.scroll-chat'),
                discussion_page = 2,
                last_page = false;

            var ws_scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
            var ws_path = ws_scheme + '://' + window.location.host + window.location.pathname;

            var socket = new ReconnectingWebSocket(ws_path, null, {maxReconnectAttempts: 5, timeoutInterval: 5000});

            socket.onmessage = function(message) {
                var data = JSON.parse(message.data);

                if (data['sender'] !== chat.data('sender-id')) {
                    chat.append(data['data']);
                    chat.animate({scrollTop: ($('.item', chat).length * $('.item', chat).outerHeight())}, 0, 'swing');

                    var new_messages_counter = $('.nav-advertise .number'),
                        messages_count = parseInt(new_messages_counter.text());

                    new_messages_counter.text(messages_count + 1);
                }
            };

            socket.onopen = function() {
                console.log('OPEN');
            };

            chat.animate({scrollTop: ($('.item', chat).length * $('.item', chat).outerHeight())}, 0, 'swing', function() {
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
                e.preventDefault();

                var message_form = $(this);

                $('.error', message_form).removeClass('error');

                if (!$.trim($('textarea[name="message"]', message_form).val())) {
                    $('textarea[name="message"]', message_form).addClass('error');

                    return false;
                }

                $.post(chat.data('messages-url'), message_form.serialize(), function(response) {
                    if (response['success']) {
                        chat.append(response['data']);
                        chat.animate({scrollTop: ($('.item', chat).length * $('.item', chat).outerHeight())}, 0, 'swing');

                        message_form.trigger('reset');
                    }
                }, 'json');
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

            $(document).on('click', '.thumb__favorite', function(e) {
                e.preventDefault();

                var link = $(this);

                $.post(link.data('favorite-url'), {'favorite_id': link.data('item-id')}, function(response) {
                    if (response['success']) {
                        var url = new URI(window.location.href);

                        url.query('');

                        load_data(url, {}, $('.items'));
                    }
                }, 'json');
            });
        }

        // Account settings page handlers
        if ($('.sidebar-user_cabinet').length) {
            jcf.replaceAll();
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
            e.preventDefault();

            if (is_user_authenticated()) {
                $('#model-user_message').fadeIn(200);
            } else {
                modal(gettext('You must be logged to perform this operation'));
            }
        });

        $('.hint-info_box .close-btn').on('click' , function() {
            $(this).parent().removeClass('show');
        });


        function load_data(url, data, element) {
            var content = typeof element != 'undefined' ? element : $('.inner__content');

            $('html, body').animate({scrollTop: 0});

            preloader_show();

            window.history.pushState('', '', url);

            $.get(url, data, function(response) {
                if (response['success']) {
                    $(content).empty().append(response['data']);
                }

                if (response['page_seo_information']) {
                    if (response['page_seo_information']['meta_title']) {
                        $('title').text(response['page_seo_information']['meta_title']);
                    }

                    if (response['page_seo_information']['meta_description']) {
                        $('meta[name="description"]').attr('content', response['page_seo_information']['meta_description']);
                    }

                    if (response['page_seo_information']['meta_keywords']) {
                        $('meta[name="keywords"]').attr('content', response['page_seo_information']['meta_keywords']);
                    }
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

        function is_user_authenticated() {
            return $('body').data('user-authenticated');
        }

        function modal(message) {
            var modal = $('#think-model');

            $('.message', modal).empty().text(message);
            modal.fadeIn(200);
        }

        function check_link(link) {
            var result = {'success': true, 'error': ''},
                link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

            if (!link) {
                result = {
                    'success': false,
                    'error': gettext('This field is required')
                };
            } else {
                var url_info = new URI(link),
                    is_valid = false,
                    social_networks = {
                        'vk': {
                            'hosts': ['m.vk.com', 'vk.com', 'www.vk.com'],
                            'patterns': [/^https:\/\/vk\.com\/[a-zA-Z0-9-_.]+\/?$/g],
                            'valid_pattern': 'https://vk.com/xxxxxxx'
                        },
                        'youtube': {
                            'hosts': ['www.youtube.com', 'youtube.com', 'm.youtube.com'],
                            'patterns': [/^https:\/\/www\.youtube\.com\/channel\/[a-zA-Z0-9-_]+\/?$/g],
                            'valid_pattern': 'https://www.youtube.com/channel/xxxxxxx'
                        },
                        'facebook': {
                            'hosts': ['www.facebook.com', 'facebook.com', 'm.facebook.com'],
                            'patterns': [
                                /^https:\/\/www\.facebook\.com\/groups\/[a-zA-Z0-9-_]+\/?$/g,
                                /^https:\/\/www\.facebook\.com\/[a-zA-Z0-9-_]+\/?$/g
                            ],
                            'valid_pattern': 'https://www.facebook.com/xxxxxxx, https://www.facebook.com/groups/xxxxxxx'
                        },
                        'instagram': {
                            'hosts': ['www.instagram.com', 'instagram.com'],
                            'patterns': [/^https:\/\/www\.instagram\.com\/[a-zA-Z0-9-_.]+\/$/g],
                            'valid_pattern': 'https://www.instagram.com/xxxxxxx/'
                        },
                        'twitter': {
                            'hosts': ['www.twitter.com', 'twitter.com', 'mobile.twitter.com'],
                            'patterns': [/^https:\/\/twitter\.com\/[a-zA-Z0-9-_]+\/?$/g],
                            'valid_pattern': 'https://twitter.com/xxxxxxx'
                        },
                        'telegram': {
                            'hosts': ['www.t.me', 't.me'],
                            'patterns': [
                                /^https:\/\/t\.me\/[a-zA-Z0-9_]+\/?$/g,
                                /^https:\/\/www\.t\.me\/[a-zA-Z0-9_]+\/?$/g
                            ],
                            'valid_pattern': 'https://www.t.me/xxxxxxx, https://t.me/xxxxxxx'
                        }
                    };

                for (var social_network in social_networks) {
                    var hosts = social_networks[social_network]['hosts'],
                        patterns = social_networks[social_network]['patterns'],
                        valid_pattern = social_networks[social_network]['valid_pattern'];

                    if (hosts.indexOf(url_info.hostname()) !== -1) {
                        for (var index in patterns) {
                            var pattern = patterns[index];

                            if (pattern.test(url_info)) {
                                is_valid = true;

                                break;
                            }
                        }

                        if (!is_valid) {
                            var msg = gettext('Seems you wrote incorrect link. The link should be in the format ');

                            result = {
                                'success': false,
                                'error': msg + valid_pattern
                            };
                        }
                    }
                }

                if (!is_valid && result['success']) {
                    result = {
                        'success': false,
                        'error': gettext('You have inserted an incorrect value for the link to the page, group or account that you are selling *')
                    };
                }
            }

            return result;
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