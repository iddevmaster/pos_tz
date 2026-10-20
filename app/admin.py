from django.contrib import admin

from .models import InternalMemoCategory


@admin.register(InternalMemoCategory)
class InternalMemoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
