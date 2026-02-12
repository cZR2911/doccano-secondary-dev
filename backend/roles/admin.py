from django.contrib import admin

from .models import Feature, Role


class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    ordering = ("name",)
    search_fields = ("name",)


class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    ordering = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("features",)


admin.site.register(Feature, FeatureAdmin)
admin.site.register(Role, RoleAdmin)
