from django.urls import path
from . import views

app_name = 'bulk_operations'

urlpatterns = [
    path('csv-import/', views.csv_import_questions, name='csv_import'),
    path('csv-validate/', views.csv_validate, name='csv_validate'),
    path('csv-preview/', views.csv_preview, name='csv_preview'),
    path('csv-template/', views.csv_template_download, name='csv_template'),
]