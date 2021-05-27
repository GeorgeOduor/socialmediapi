from django.contrib import admin

# Register your models here.
from .models import SocialMediaDataset
from import_export.admin import ImportExportModelAdmin

admin.site.register(SocialMediaDataset,ImportExportModelAdmin)