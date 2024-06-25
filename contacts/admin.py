from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('odoo_id', 'name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('name',)
    ordering = ('name',)

admin.site.register(Contact, ContactAdmin)
