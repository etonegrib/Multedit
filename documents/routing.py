from django.urls import re_path
from .consumers import DocConsumer

websocket_urlpatterns = [
    re_path(r"^ws/doc/(?P<doc_id>\d+)/$", DocConsumer.as_asgi()),
]