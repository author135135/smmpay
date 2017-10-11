from channels import Group
from channels.auth import channel_session_user_from_http


@channel_session_user_from_http
def ws_connect(message, *args, **kwargs):
    message.reply_channel.send({"accept": True})

    group_keyword = 'discussion-{}'.format(kwargs['pk'])
    Group(group_keyword).add(message.reply_channel)


@channel_session_user_from_http
def ws_disconnect(message, *args, **kwargs):
    group_keyword = 'discussion-{}'.format(kwargs['pk'])
    Group(group_keyword).discard(message.reply_channel)
