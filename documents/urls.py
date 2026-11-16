from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_doc, name="create_doc"),
    path("doc/<int:doc_id>/", views.doc_view, name="doc_view"),
    path("doc/<int:doc_id>/upload-image/", views.upload_image, name="upload_image"),
]