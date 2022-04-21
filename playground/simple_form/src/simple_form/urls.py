from django.urls import path
from .views import raw, only_mapping, view, validation

app_name = 'form'

urlpatterns = [
    path('raw', raw.get, name='raw_get'),
    path('raw_post', raw.post, name='raw_post'),

    path('only_mapping', only_mapping.get, name='only_mapping_get'),
    path('only_mapping_post', only_mapping.post, name='only_mapping_post'),

    path('view', view.get, name='view_get'),
    path('view_post', view.post, name='view_post'),

    path('validation', validation.get, name='validation_get'),
    path('validation_post', validation.post, name='validation_post'),
]
