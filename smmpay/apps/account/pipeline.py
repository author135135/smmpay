def save_profile(backend, user, response, *args, **kwargs):
    if not user.profile.first_name:
        first_name = ''

        if backend.name == 'google-oauth2':
            first_name = response.get('given_name')
        elif backend.name == 'facebook':
            first_name = response.get('name')
        elif backend.name == 'vk':
            first_name = response.get('first_name')

        if first_name:
            user.profile.first_name = first_name
            user.profile.save()
