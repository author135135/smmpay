from channels import include


channel_routing = [
    include('smmpay.apps.account.routing.websocket_routing', path=r'^/account/discussion/(?P<pk>[0-9]+)/$')
]
