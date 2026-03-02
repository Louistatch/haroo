from django.contrib import admin
from .models import Region, Prefecture, Canton


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'created_at']
    search_fields = ['nom', 'code']
    ordering = ['nom']


@admin.register(Prefecture)
class PrefectureAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'region', 'created_at']
    list_filter = ['region']
    search_fields = ['nom', 'code']
    ordering = ['nom']


@admin.register(Canton)
class CantonAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'prefecture', 'created_at']
    list_filter = ['prefecture__region', 'prefecture']
    search_fields = ['nom', 'code']
    ordering = ['nom']
