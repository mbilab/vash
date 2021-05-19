from django.contrib import admin

from .models import CohortModel, HashCodeModel, VariantModel

# Register your models here.
admin.site.register(CohortModel)
admin.site.register(VariantModel)
admin.site.register(HashCodeModel)
