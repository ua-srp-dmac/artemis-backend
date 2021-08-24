from django.contrib import admin
from .models import *

class SiteAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )

class PlotAdmin(admin.ModelAdmin):
    list_display = (
        'site',
    )

class ReplicateAdmin(admin.ModelAdmin):
    list_display = (
        'plot', 'label'
    )

class MineralogyAdmin(admin.ModelAdmin):
    list_display = (
        'site', 'collection_date', 'time_label', 'min_depth', 'max_depth'
    )

class GeochemistryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'site', 'replicate', 'collection_date', 'time_label', 'min_depth', 'max_depth'
    )

class ExtractionAdmin(admin.ModelAdmin):
    list_display = (
        'site', 'collection_date', 'time_label', 'element', 'min_depth', 'max_depth'
    )


admin.site.register(Site, SiteAdmin)
admin.site.register(Plot, PlotAdmin)
admin.site.register(Replicate, ReplicateAdmin)
admin.site.register(Mineralogy, MineralogyAdmin)
admin.site.register(Geochemistry, GeochemistryAdmin)
admin.site.register(Extraction, ExtractionAdmin)
