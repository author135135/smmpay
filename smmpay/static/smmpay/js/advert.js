(function ($) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    var form = $('#advert-add-form'),
        form_type = $('input[name="advert_type"]', form).val();

    if (form_type === 'social_account') {
        $('input[name="link"]', form).on('focusout', function(e) {
            var field = $(this),
                parent_block = field.parents('.form-group'),
                url = $(this).val();

            $('.help-block', parent_block).remove();
            parent_block.removeClass('has-error');

            $('#account-info', form).empty();

            $('.hidden-field input', form).val('');

            if (!$('.hidden-field', form).hasClass('hidden')) {
                $('.hidden-field', form).addClass('hidden');
            }

            if (!url.match(/http(s)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g)) {
                parent_block.addClass('has-error');
                parent_block.append('<span class="help-block">Enter correct url address</span>');

                return false;
            }

            var request_data = {
                'account_link': url
            };

            $.get('/advert/add/social-account/info/', request_data, function(response) {
                if (response['success']) {
                    $.each(response['fields'], function(field, value) {
                        var form_field = $('input[name="' + field + '"]', form);

                        if (value) {
                            $(form_field).val(value);
                        } else {
                            $(form_field).parents('.form-group').removeClass('hidden');
                        }
                    });

                    $('#account-info', form).html(response['data']);
                } else {
                    $('.hidden-field', form).removeClass('hidden');
                }
            }, 'json');
        });
    }

    function getCookie (name) {
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
}(jQuery));