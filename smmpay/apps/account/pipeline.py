import logging
import json

logger = logging.getLogger('db')


def save_profile(backend, user, response, *args, **kwargs):
    logger.info("BACKEND: {}\n DATA: {}".format(backend.name, json.dumps(response)))

    if not user.profile.first_name:
        first_name = ''

        if backend.name == 'google-oauth2':
            first_name = response.get('given_name')
        elif backend.name == 'facebook':
            first_name = response.get('name')
        elif backend.name == 'vk':
            pass

        if first_name:
            user.profile.first_name = first_name
            user.profile.save()
