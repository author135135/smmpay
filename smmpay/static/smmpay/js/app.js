(function ($) {
    $(document).ready(function(e) {
        var process_in_progress = 0;

        $.ajaxSetup({
            cache: false
        });

        if ($('.sidebar:not(.sidebar-user_cabinet)').length) {
            var stickSidebar;

            $(window).on('resize', function(e) {
                if (window.innerWidth <= 979 && typeof stickSidebar !== "undefined") {
                    stickSidebar.stickySidebar('destroy');
                    stickSidebar = undefined;
                } else if (window.innerWidth > 979 && typeof stickSidebar === "undefined") {
                    stickSidebar = $('.sidebar').stickySidebar({
                        topSpacing: 20,
                        bottomSpacing: 20
                    }).stickySidebar('initialize');
                }
            }).resize();
        }

        if ($('.login').length) {
            $('.login').click(function(e) {
                if (is_user_authenticated()) {
                    e.preventDefault();

                    $('.account-dropdown-menu-wrapper').toggleClass('visible');
                }
            });

            $(document).on('click', function(e) {
                if (!$(e.target).closest('.login').length && !$(e.target).closest('.account-dropdown-menu-wrapper').length) {
                    $('.account-dropdown-menu-wrapper').removeClass('visible');
                }
            });
        }

        $('.to-top').click(function(e) {
            $('html, body').animate({scrollTop:0}, '300');
        });

        $(window).on('scroll', function(e) {
            if ($(window).scrollTop() > 500) {
                $('.to-top').addClass('visible');
            } else {
                $('.to-top').removeClass('visible');
            }
        }).scroll();

        // Filter form handlers
        if ($('.filter-form').length) {
            $("#id_category, #id_service").select2({
                tags: true
            });

            $("#id_category, #id_service").on('select2:close', function(e) {
                var wrapper = $(this).next();

                if (e.target.options.length !== 0 && e.target.options.length !== e.target.selectedOptions.length) {
                    $('.select2-search__field', wrapper).attr('placeholder', gettext('More...'));
                }
            });

            $("#id_category, #id_service").trigger('select2:close');

            var ddSlickInitCall1 = true;

            $('#id_social_network').ddslick({
                imagePosition: 'left',
                onSelected: function(selectedData){
                    if ($('#id_social_network .dd-select').hasClass(selectedData['selectedData']['value']) || process_in_progress) {
                        return false;
                    }

                    $('#id_social_network .dd-select').attr('class', 'dd-select');
                    $('#id_social_network .dd-select').addClass(selectedData['selectedData']['value']);
                    $('.side__filter__container .filter-form .social-network').text(selectedData['selectedData']['text']);

                    if (ddSlickInitCall1 === true) {
                        ddSlickInitCall1 = false;
                        return false;
                    }

                    $('.filter-form input').val('');
                    $('.filter-form select:not(#id_category)').val('').trigger('change');

                    processAppliedFilters();

                    var url = new URI(window.location.href);
                    url.path(selectedData['selectedData']['value'] + '/').query('').hash('');

                    load_data(url, {}, $('.items'), true);
                }
            });

            var ddSlickInitCall2 = true;

            $('#sort_by').ddslick({
                imagePosition: 'right',
                onSelected: function(selectedData){
                    var current_value = $('#sort_by').data('current-value'),
                        selected_value = selectedData['selectedData']['value'];

                    if (current_value === selected_value || process_in_progress) {
                        return false;
                    }

                    $('#sort_by').data('current-value', selected_value);

                    if (ddSlickInitCall2 === true) {
                        ddSlickInitCall2 = false;
                        return false;
                    }

                    var url = new URI(window.location.href),
                        url_query = url.query(true);

                    url_query['sort_by'] = selectedData['selectedData']['value'];
                    url.query(url_query);

                    load_data(url, {}, $('.items'));
                }
            });

            processAppliedFilters();

            $('.filter__reset').on('click', function () {
                var need_reload = false;

                $('.filter-form input').val('');

                $('.filter-form select').val('').trigger('change');

                var url = new URI(window.location.href),
                    url_query = url.query(true);

                processAppliedFilters();

                if (!url_query.hasOwnProperty('page') && Object.keys(url_query).length || Object.keys(url_query).length > 1) {
                    url.query({});
                    need_reload = true;
                }

                $('.filter__form-social a').each(function() {
                    var link_url = new URI($(this).attr('href'));
                    link_url.query({});

                    $(this).attr('href', link_url);
                });

                if ($(this).closest('.side__filter__container').length) {
                    $('.side__filter__container .close-btn').click();
                }

                if (need_reload) {
                    load_data(url, {}, $('.items'));
                }
            });

            $('.filter-form').on('submit', function (e) {
                e.preventDefault();

                if (process_in_progress) {
                    return false;
                }

                var url = new URI(window.location.href),
                    url_query = url.query(true),
                    query = {};

                processAppliedFilters();

                $.each($('.filter-form').serializeArray(), function(index, item) {
                    if (item.value) {
                        if (query.hasOwnProperty(item.name)) {
                            if (typeof query[item.name] !== "object") {
                                var tmp_value = query[item.name];
                                query[item.name] = [tmp_value];
                            }

                            query[item.name].push(item.value)
                        } else {
                            query[item.name] = item.value;
                        }
                    }
                });

                if (url_query['sort_by']) {
                    query['sort_by'] = url_query['sort_by'];
                }

                url.query(query);

                $('.filter__form-social a').each(function() {
                    var link_url = new URI($(this).attr('href'));

                    if (query['category']) {
                        link_url.query({'category': query['category']});
                    }

                    $(this).attr('href', link_url);
                });

                if ($(this).closest('.side__filter__container').length) {
                    $('.side__filter__container .close-btn').click();
                }

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

            $('.filter__button').click(function(e) {
                $('body').addClass('visible-sidebar');
            });

            $('.side__filter__container .close-btn').click(function(e) {
		        $('body').removeClass('visible-sidebar');
            });

            $('.currency .currency__current').click(function(e) {
                e.preventDefault();

                var menu = $(this).parents('.currency').find('.currency__list');

                menu.stop().slideDown(200);
            });

            $(document).on('click', function(e) {
                if (!$(e.target).closest('.currency').length) {
                    $('.currency .currency__list').stop().slideUp(100);
                }
            });
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

            $("select").select2({
                minimumResultsForSearch: -1
            });

            autosize($('textarea[name="description"]', advert_add_form));

            new ClipboardJS('button.copy');

            processNegotiatedPriceFields();

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

                $('.update-info').hide();

                $('.error_input', wrapper).remove();
                $('.hidden-field .error_input', advert_add_form).remove();

                info_table.empty();
                info_table.addClass('hidden');

                $('.hidden-field input', advert_add_form).val('');
                $('input[name="external_logo"]', advert_add_form).val('');

                $('select[name^="social_account_services"] option:not(:first-child)').remove();
                $('select[name^="social_account_services"]').val('');
                $('input[type="number"][name^="social_account_services"]').val('');

                $('.item.avatar .item__field .thumb__avatar').remove();
                $('.verification-status', advert_add_form).remove();

                $("select").select2({
                    minimumResultsForSearch: -1
                });

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

                            if (value != null) {
                                $(form_field).val(value);

                                if (field === 'external_logo') {
                                    $('.item.avatar .item__field').prepend('<a class="thumb__avatar"><img src="' + value + '"></a>');
                                    $('.filename').text('').hide();
                                    $('.file-upload span').text(gettext('Change'));
                                }
                            } else {
                                if (field === 'external_logo') {
                                    $('.filename').text(gettext('Logo not uploaded')).show();
                                    $('.file-upload span').text(gettext('Download from device'));
                                }
                            }
                        });
                    } else {
                        $('.filename').text(gettext('Logo not uploaded')).show();
                        $('.file-upload span').text(gettext('Download from device'));
                    }

                    $('.item.hidden', advert_add_form).removeClass('hidden');

                    link_check_progress = 0;

                    $('.update-info').show();
                    preloader_hide();
                }, 'json');

                $.get(advert_add_form.data('services-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        var option_html = '';

                        $.each(response['services'], function(idx, item) {
                            option_html += '<option value="' + item[0] + '">' + item[1] + '</option>';
                        });

                        $('select[name^="social_account_services"]').append(option_html);
                    }
                }, 'json');
            });

            $('.update-button', advert_add_form).on('click', function(e) {
                e.preventDefault();

                var field = $('input[name="link"]', advert_add_form);

                if (link_check_progress) {
                    return false;
                }

                link = $.trim(field.val());

                link_check_progress = 1;

                preloader_show();

                $.get(advert_add_form.data('validation-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        $.each(response['fields'], function(field, value) {
                            var form_field = $('input[name="' + field + '"]', advert_add_form);

                            if (value != null) {
                                $(form_field).val(value);

                                if (field === 'external_logo') {
                                    $('.item.avatar .item__field .thumb__avatar').remove();
                                    $('.item.avatar .item__field').prepend('<a class="thumb__avatar"><img src="' + value + '"></a>');
                                    $('.filename').text('').hide();
                                    $('.file-upload span').text(gettext('Change'));
                                }
                            } else {
                                if (field === 'external_logo') {
                                    $('.filename').text(gettext('Logo not uploaded')).show();
                                    $('.file-upload span').text(gettext('Download from device'));
                                }
                            }
                        });
                    } else {
                        $('.filename').text(gettext('Logo not uploaded')).show();
                        $('.file-upload span').text(gettext('Download from device'));
                    }

                    link_check_progress = 0;

                    preloader_hide();
                }, 'json');
            });

            $('input[type="file"]', advert_add_form).on('change', function(e) {
                if (e.target.value) {
                    var fileName = e.target.value.split('\\').pop();
                    $('.filename', advert_add_form).text(fileName).show();

                    if ($('.thumb__avatar').length) {
                        $('.thumb__avatar').hide();
                    }
                } else {
                    $('.filename', advert_add_form).text('').hide();

                    if ($('.thumb__avatar').length) {
                        $('.thumb__avatar').show();
                    }
                }
            });

            $('.add-service').on('click', function(e) {
                e.preventDefault();

                $('select').each(function(e) {
                    $(this).select2('destroy');
                });

                var wrapper = $(this).parents('.item'),
                    form_idx = $('#id_social_account_services-TOTAL_FORMS').val();

                wrapper.before($('.empty-formset').html().replace(/__prefix__/g, form_idx));

                $('#id_social_account_services-TOTAL_FORMS').val(parseInt(form_idx) + 1);

                $('select').select2({
                    minimumResultsForSearch: -1
                });
            });

            $(document).on('click', '.remove-service', function(e) {
                e.preventDefault();

                var form_idx = $('#id_social_account_services-TOTAL_FORMS').val();
                $('#id_social_account_services-TOTAL_FORMS').val(parseInt(form_idx) - 1);

                $(this).parents('.item').remove();
            });

            $(document).on('click', '.negotiated-price input', function(e) {
                processNegotiatedPriceFields();
            });

            $('.confirm-button').click(function(e) {
                var link = $.trim($('input[name="link"]').val()),
                    button = $(this);

                if (link_check_progress) {
                    return false;
                }

                $('.error_input', advert_add_form).remove();
                $('.verification-status', advert_add_form).remove();

                if (!link) {
                    $('.confirm-button-wrapper', advert_add_form).after('<div class="error_input">' + gettext('Field `link` is empty. Please fill it before send link to confirmation') + '</div>');

                    return false;
                }

                link_check_progress = 1;
                button.next().show();

                var postData = {
                    account_link: link,
                    confirm_code: $.trim($('.code-button span', advert_add_form).text())
                };

                $.post(button.data('confirm-url'), postData, function(response) {
                    if (response['success']) {
                        if (response['confirmed'] === true) {
                            $('.confirm-button-wrapper', advert_add_form).after('<div class="verification-status success">' + gettext('Site successfully verified') + '</div>');
                        } else {
                            $('.confirm-button-wrapper', advert_add_form).after('<div class="verification-status fail">' + gettext('Site is not verified') + '</div>');
                        }
                    }

                    link_check_progress = 0;
                    button.next().hide();
                }, 'json');
            });

            advert_add_form.submit(function(e) {
                var error = 0,
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                $('.error_input', advert_add_form).remove();

                var result = check_link(link);

                if (!result['success']) {
                    $('input[name="link"]', advert_add_form).parent().append('<div class="error_input">' + result['error'] + '</div>');

                    error = 1;
                }

                if (!$('select[name="category"]', advert_add_form).val()) {
                    error = 1;

                    $('select[name="category"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="price"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="price"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                var services = [];

                $('#advert-add-form > .service-item').each(function(e) {
                    var service_wrapper = $(this),
                        service_val = $('select', service_wrapper).val(),
                        price_val = $('input[type="number"]', service_wrapper).val(),
                        negotiated_price = $('.negotiated-price input[type="checkbox"]', service_wrapper).prop('checked');

                    if (service_val) {
                        var elem_idx = services.indexOf(service_val);

                        if (elem_idx !== -1) {
                            error = 1;

                            $('select', service_wrapper).parent().append('<div class="error_input">' + gettext('This value already selected') + '</div>');
                        } else {
                            services.push(service_val);
                        }

                        if (!price_val && !negotiated_price) {
                            error = 1;

                            $('input[type="number"]', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                        }
                    }

                    if ((price_val || negotiated_price) && !service_val) {
                        error = 1;

                        $('select', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                    }
                });

                if (services.length === 0) {
                    var service_wrapper = $('#advert-add-form > .service-item:first');

                    error = 1;

                    $('.error_input', service_wrapper).remove();

                    $('select', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                    $('input[type="number"]', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && !$('input[name="title"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="title"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && $.trim($('input[name="subscribers"]', advert_add_form).val()) === "") {
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

            $("select").select2({
                minimumResultsForSearch: -1
            });

            autosize($('textarea[name="description"]', advert_edit_form));

            new ClipboardJS('button.copy');

            processNegotiatedPriceFields();

            var link = $('input[name="link"]', advert_edit_form).val() ? $('input[name="link"]', advert_edit_form).val(): '',
                link_check_progress = 0;

            $('input[name="link"]', advert_edit_form).on('focusout', function(e) {
                var field = $(this),
                    wrapper = field.parent(),
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                if (link == $.trim(field.val()) || link_check_progress) {
                    return false;
                }

                link = $.trim($(this).val());

                $('.update-info').hide();
                $('.hidden-field .error_input', advert_add_form).remove();
                $('.error_input', wrapper).remove();

                $('.hidden-field input', advert_edit_form).val('');
                $('input[name="external_logo"]', advert_edit_form).val('');

                $('select[name^="social_account_services"] option:not(:first-child)').remove();
                $('select[name^="social_account_services"]').val('');
                $('input[type="number"][name^="social_account_services"]').val('');

                $('.item.avatar .item__field .thumb__avatar').remove();
                $('.verification-status', advert_edit_form).remove();

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

                            if (value != null) {
                                $(form_field).val(value);

                                if (field === 'external_logo') {
                                    $('.item.avatar .item__field').prepend('<a class="thumb__avatar"><img src="' + value + '"></a>');
                                    $('.filename').text('').hide();
                                    $('.file-upload span').text(gettext('Change'));
                                }
                            } else {
                                if (field === 'external_logo') {
                                    $('.filename').text(gettext('Logo not uploaded')).show();
                                    $('.file-upload span').text(gettext('Download from device'));
                                }
                            }
                        });
                    } else {
                        $('.filename').text(gettext('Logo not uploaded')).show();
                        $('.file-upload span').text(gettext('Download from device'));
                    }

                    link_check_progress = 0;

                    $('.update-info').show();
                    preloader_hide();
                }, 'json');

                $.get(advert_edit_form.data('services-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        var option_html = '';

                        $.each(response['services'], function(idx, item) {
                            option_html += '<option value="' + item[0] + '">' + item[1] + '</option>';
                        });

                        $('select[name^="social_account_services"]').append(option_html);
                    }
                }, 'json');

                $('select').select2({
                    minimumResultsForSearch: -1
                });
            });

            $('.update-button', advert_edit_form).on('click', function(e) {
                e.preventDefault();

                var field = $('input[name="link"]', advert_edit_form);

                if (link_check_progress) {
                    return false;
                }

                link = $.trim(field.val());

                link_check_progress = 1;

                preloader_show();

                $.get(advert_edit_form.data('validation-url'), {account_link: link}, function(response) {
                    if (response['success']) {
                        $.each(response['fields'], function(field, value) {
                            var form_field = $('input[name="' + field + '"]', advert_edit_form);

                            if (value != null) {
                                $(form_field).val(value);

                                if (field === 'external_logo') {
                                    $('.item.avatar .item__field .thumb__avatar').remove();
                                    $('.item.avatar .item__field').prepend('<a class="thumb__avatar"><img src="' + value + '"></a>');
                                    $('.filename').text('').hide();
                                    $('.file-upload span').text(gettext('Change'));
                                }
                            } else {
                                if (field === 'external_logo') {
                                    $('.filename').text(gettext('Logo not uploaded')).show();
                                    $('.file-upload span').text(gettext('Download from device'));
                                }
                            }
                        });
                    } else {
                        $('.filename').text(gettext('Logo not uploaded')).show();
                        $('.file-upload span').text(gettext('Download from device'));
                    }

                    link_check_progress = 0;

                    preloader_hide();
                }, 'json');
            });

            $('input[type="file"]', advert_edit_form).on('change', function(e) {
                if (e.target.value) {
                    var fileName = e.target.value.split('\\').pop();
                    $('.filename').text(fileName).show();

                    if ($('.thumb__avatar').length) {
                        $('.thumb__avatar').hide();
                    }
                } else {
                    $('.filename').text('').hide();

                    if ($('.thumb__avatar').length) {
                        $('.thumb__avatar').show();
                    }
                }
            });

            $('.add-service').on('click', function(e) {
                e.preventDefault();

                $('select').each(function(e) {
                    $(this).select2('destroy');
                });

                var wrapper = $(this).parents('.item'),
                    form_idx = $('#id_social_account_services-TOTAL_FORMS').val();

                wrapper.before($('.empty-formset').html().replace(/__prefix__/g, form_idx));

                $('#id_social_account_services-TOTAL_FORMS').val(parseInt(form_idx) + 1);

                $('select').select2({
                    minimumResultsForSearch: -1
                });
            });

            $(document).on('click', '.remove-service', function(e) {
                e.preventDefault();

                var wrapper = $(this).parents('.item'),
                    form_idx = $('#id_social_account_services-TOTAL_FORMS').val(),
                    new_form_idx = parseInt(form_idx) - 1,
                    initial_forms = $('#id_social_account_services-INITIAL_FORMS').val();


                if (new_form_idx < initial_forms) {
                    new_form_idx = initial_forms;
                }

                if (wrapper.hasClass('new_item')) {
                   wrapper.remove();
                   $('#id_social_account_services-TOTAL_FORMS').val(new_form_idx);
                } else {
                    wrapper.addClass('hidden');
                    $('input[type="checkbox"]', wrapper).click();
                }
            });

            $(document).on('click', '.negotiated-price input', function(e) {
                processNegotiatedPriceFields();
            });

            $('.confirm-button').click(function(e) {
                var link = $.trim($('input[name="link"]').val()),
                    button = $(this);

                if (link_check_progress) {
                    return false;
                }

                $('.error_input', advert_edit_form).remove();
                $('.verification-status', advert_edit_form).remove();

                if (!link) {
                    $('.confirm-button-wrapper', advert_edit_form).after('<div class="error_input">' + gettext('Field `link` is empty. Please fill it before send link to confirmation') + '</div>');

                    return false;
                }

                link_check_progress = 1;
                button.next().show();

                var postData = {
                    account_link: link,
                    confirm_code: $.trim($('.code-button span', advert_edit_form).text())
                };

                $.post(button.data('confirm-url'), postData, function(response) {
                    if (response['success']) {
                        if (response['confirmed'] === true) {
                            $('.confirm-button-wrapper', advert_edit_form).after('<div class="verification-status success">' + gettext('Site successfully verified') + '</div>');
                        } else {
                            $('.confirm-button-wrapper', advert_edit_form).after('<div class="verification-status fail">' + gettext('Site is not verified') + '</div>');
                        }
                    }

                    link_check_progress = 0;
                    button.next().hide();
                }, 'json');
            });

            advert_edit_form.submit(function(e) {
                var error = 0,
                    link_pat = /http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;

                $('.error_input', advert_add_form).remove();

                var result = check_link(link);

                if (!result['success']) {
                    $('input[name="link"]', advert_add_form).parent().append('<div class="error_input">' + result['error'] + '</div>');

                    error = 1;
                }

                if (!$('select[name="category"]', advert_add_form).val()) {
                    error = 1;

                    $('select[name="category"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (!$('input[name="price"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="price"]', advert_add_form).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                var services = [];

                $('#advert-edit-form > .service-item:not(.hidden)').each(function(e) {
                    var service_wrapper = $(this),
                        service_val = $('select', service_wrapper).val(),
                        price_val = $('input[type="number"]', service_wrapper).val(),
                        negotiated_price = $('.negotiated-price input[type="checkbox"]', service_wrapper).prop('checked');

                    if (service_val) {
                        var elem_idx = services.indexOf(service_val);

                        if (elem_idx !== -1) {
                            error = 1;

                            $('select', service_wrapper).parent().append('<div class="error_input">' + gettext('This value already selected') + '</div>');
                        } else {
                            services.push(service_val);
                        }

                        if (!price_val && !negotiated_price) {
                            error = 1;

                            $('input[type="number"]', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                        }
                    }

                    if ((price_val || negotiated_price) && !service_val) {
                        error = 1;

                        $('select', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                    }
                });

                if (services.length === 0) {
                    var service_wrapper = $('#advert-edit-form > .service-item:first');

                    error = 1;

                    $('.error_input', service_wrapper).remove();

                    $('select', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                    $('input[type="number"]', service_wrapper).parent().append('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && !$('input[name="title"]', advert_add_form).val()) {
                    error = 1;

                    $('input[name="title"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && $.trim($('input[name="subscribers"]', advert_add_form).val()) === "") {
                    error = 1;

                    $('input[name="subscribers"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
                }

                if (result['success'] && !$('input[name="external_logo"]', advert_add_form).val() && !$('input[name="logo"]', advert_add_form).val() && $('.thumb__avatar img').length === 0) {
                    error = 1;

                    $('input[name="logo"]', advert_add_form).after('<div class="error_input">' + gettext('This field is required') + '</div>');
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

            $('.tooltip').click(function(e) {
                e.preventDefault();

                $(this).parents('.tooltip-wrapper').find('.tooltip-modal').toggleClass('visible');
            });

            $('.tooltip-close').click(function(e) {
                $(this).parents('.tooltip-modal').removeClass('visible');
            });

            $(document).on('click', function(e) {
                if (!$(e.target).closest('.tooltip-wrapper').length) {
                    $('.tooltip-modal').removeClass('visible');
                }
            });

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

            var ddSlickInitCall3 = true;

            $('#id_social_network').ddslick({
                imagePosition: 'left',
                onSelected: function(selectedData){
                    if ($('#id_social_network .dd-select').hasClass(selectedData['selectedData']['value']) || process_in_progress) {
                        return false;
                    }

                    $('#id_social_network .dd-select').attr('class', 'dd-select');
                    $('#id_social_network .dd-select').addClass(selectedData['selectedData']['value']);

                    if (ddSlickInitCall3 === true) {
                        ddSlickInitCall3 = false;
                        return false;
                    }

                    var url = new URI(window.location.href),
                        url_query = url.query(true);

                    if (url_query['page']) {
                        delete url_query['page'];
                    }

                    url_query['social_network'] = selectedData['selectedData']['value'];
                    url.query(url_query);

                    load_data(url, {}, $('.items'));
                }
            });

            var ddSlickInitCall4 = true;

            $('#sort_by').ddslick({
                imagePosition: 'right',
                onSelected: function(selectedData){
                    var current_value = $('#sort_by').data('current-value'),
                        selected_value = selectedData['selectedData']['value'];

                    if (current_value === selected_value || process_in_progress) {
                        return false;
                    }

                    $('#sort_by').data('current-value', selected_value);

                    if (ddSlickInitCall4 === true) {
                        ddSlickInitCall4 = false;
                        return false;
                    }

                    var url = new URI(window.location.href),
                        url_query = url.query(true);

                    url_query['sort_by'] = selected_value;
                    url.query(url_query);

                    $('#sort_by').parents('.sort-wrapper').data('current-value', selected_value);

                    load_data(url, {}, $('.items'));
                }
            });

            $('#account-search-form').submit(function(e) {
                e.preventDefault();

                var form = $(this),
                    url = new URI(window.location.href),
                    url_query = url.query(true);

                $.each(form.serializeArray(), function(index, item) {
                    url_query[item.name] = item.value;
                });

                url.query(url_query);

                load_data(url, {}, $('.items'));
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

            // Rewrite click event handler
            $(document).off('click', '.thumb__favorite');
            $(document).on('click', '.thumb__favorite', function(e) {
                e.preventDefault();

                var link = $(this);

                $.post(link.data('favorite-url'), {'favorite_id': link.data('item-id')}, function(response) {
                    if (response['success']) {
                        var text = $('.global-title_box h1').text(),
                            itemsCount = parseInt(text.match(/\((\d)\)/)[1]);

                            $('.global-title_box h1').text(text.replace(/\(\d\)/, '(' + (itemsCount - 1) +')'))

                        if ($('#id_social_network').length) {
                            $('#id_social_network').ddslick('destroy');

                            text = $('#id_social_network option:selected').text(),
                            itemsCount = parseInt(text.match(/\((\d)\)/)[1]);

                            $('#id_social_network option:selected').text(text.replace(/\(\d\)/, '(' + (itemsCount - 1) +')'))

                            var ddSlickInitCall3 = true;

                            $('#id_social_network').ddslick('destroy');

                            $('#id_social_network').ddslick({
                                imagePosition: 'left',
                                onSelected: function(selectedData){
                                    if ($('#id_social_network .dd-select').hasClass(selectedData['selectedData']['value']) || process_in_progress) {
                                        return false;
                                    }

                                    $('#id_social_network .dd-select').attr('class', 'dd-select');
                                    $('#id_social_network .dd-select').addClass(selectedData['selectedData']['value']);

                                    if (ddSlickInitCall3 === true) {
                                        ddSlickInitCall3 = false;
                                        return false;
                                    }

                                    var url = new URI(window.location.href),
                                        url_query = url.query(true);

                                    if (url_query['page']) {
                                        delete url_query['page'];
                                    }

                                    url_query['social_network'] = selectedData['selectedData']['value'];
                                    url.query(url_query);

                                    load_data(url, {}, $('.items'));
                                }
                            });
                        }

                        var url = new URI(window.location.href),
                            url_query = url.query(true);

                        if (url_query['page']) {
                            delete(url_query['page']);
                        }

                        url.query(url_query);

                        load_data(url, {}, $('.items'));
                    }
                }, 'json');
            });
        }

        // Blog handlers
        if ($('.content-blog').length) {
            $(document).on('click', '.pagination__link', function(e) {
                e.preventDefault();

                var url = new URI($(this).attr('href'));

                load_data(url, {}, $('.blog-items'));
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


        function load_data(url, data, element, servicesReload) {
            var content = typeof element != 'undefined' ? element : $('.inner__content');

            $('html, body').animate({scrollTop: 0});

            preloader_show();

            window.history.pushState('', '', url);

            $.get(url, data, function(response) {
                if (response['success']) {
                    $(content).empty().append(response['data']);

                    if (response.hasOwnProperty('items_count')) {
                        $('#items-count').text(response['items_count']);
                    }

                    if (response.hasOwnProperty('service') && servicesReload === true) {
                        var option_html = '';

                        $.each(response['service'], function(idx, item) {
                            option_html += '<option value="' + item[0] + '">' + item[1] + '</option>';
                        });

                        $('#id_service option').remove();
                        $('#id_service').append(option_html);

                        $("#id_service").select2({
                            tags: true
                        });
                    }
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
                            'patterns': [/^https:\/\/www\.youtube\.com\/(channel|user)\/[a-zA-Z0-9-_]+\/?$/g],
                            'valid_pattern': 'https://www.youtube.com/channel/xxxxxxx, https://www.youtube.com/user/xxxxxxx'
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
                                /^https:\/\/www\.t\.me\/[a-zA-Z0-9_]+\/?$/g,
                                /^https:\/\/t\.me\/joinchat\/[a-zA-Z0-9_]+\/?$/g
                            ],
                            'valid_pattern': 'https://www.t.me/xxxxxxx, https://t.me/xxxxxxx, https://t.me/joinchat/xxxxxxx'
                        },
                        'tiktok': {
                            'hosts': ['www.tiktok.com', 'tiktok.com'],
                            'patterns': [
                                /^https:\/\/www\.tiktok\.com\/@[a-zA-Z0-9_.]+\/?$/g,
                                /^https:\/\/tiktok\.com\/@[a-zA-Z0-9_.]+\/?$/g
                            ],
                            'valid_pattern': 'https://www.tiktok.com/@xxxxxxx, https://tiktok.com/@xxxxxxx'
                        },
                        'twitch': {
                            'hosts': ['www.twitch.tv', 'twitch.tv'],
                            'patterns': [
                                /^https:\/\/www\.twitch\.tv\/[a-zA-Z0-9_.]+\/?$/g,
                                /^https:\/\/twitch\.tv\/[a-zA-Z0-9_.]+\/?$/g
                            ],
                            'valid_pattern': 'https://www.twitch.tv/xxxxxxx, https://twitch.tv/xxxxxxx'
                        }
                    };

                url_info.query('');
                url_info.fragment('');

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
                        'error': gettext('You have inserted an incorrect value for the link to the page, group or account *')
                    };
                }
            }

            return result;
        }

        function processNegotiatedPriceFields() {
            $('.negotiated-price input').each(function(e) {
                var negotiated_price = $(this).prop('checked');

                if (negotiated_price === false) {
                    $(this).parents('.item__field').find('.log__input').prop('disabled', '').removeClass('disabled');
                } else {
                    $(this).parents('.item__field').find('.log__input').prop('disabled', 'disabled').addClass('disabled');
                }
            });
        }

        function processAppliedFilters() {
            var appliedFilters = [];

            if ($('select[name="category"]').val()) {
                var select_value = [];

                $('select[name="category"] option:selected').each(function(idx, val) {
                    select_value.push($(this).text());
                });

                if (select_value.length) {
                    appliedFilters.push(select_value.join(', '));
                }
            }

            if ($('select[name="service"]').val()) {
                var select_value = [];

                $('select[name="service"] option:selected').each(function(idx, val) {
                    select_value.push($(this).text());
                });

                if (select_value.length) {
                    appliedFilters.push(select_value.join(', '));
                }
            }

            if ($('input[name="search_query"]').val()) {
                appliedFilters.push('"' + $('input[name="search_query"]').val() + '"');
            }

            if ($('input[name="subscribers_min"]').val() || $('input[name="subscribers_max"]').val()) {
                var args = [];

                if ($('input[name="subscribers_min"]').val()) {
                    args.push($('input[name="subscribers_min"]').val())
                } else {
                    args.push('...');
                }

                if ($('input[name="subscribers_max"]').val()) {
                    args.push($('input[name="subscribers_max"]').val())
                } else {
                    args.push('...');
                }

                appliedFilters.push(interpolate(gettext('subscribers %s-%s'), args));
            }

            if ($('input[name="price"]').val()) {
                appliedFilters.push(interpolate(gettext('price, from %s'), [$('input[name="price"]').val()]));
            }

            if (appliedFilters.length) {
                $('.applied-filters .filters').html('<span class="hidden-sm">' + gettext('Filter by') + ':</span> ' + appliedFilters.join('; '));
            } else {
                $('.applied-filters .filters').html('');
            }
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