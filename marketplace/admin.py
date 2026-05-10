from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product
from .models import Product, Category

class CustomUserAdmin(UserAdmin):
    # This adds your new fields to the "Personal Info" section in Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Celestial Profile', {'fields': ('image',)}),
        ('Store Details', {'fields': ('is_official_store', 'is_student_seller', 'store_name')}),
    )
# This makes your custom User (with Student/Vendor flags) show up
admin.site.register(User, CustomUserAdmin)

admin.site.register(Category)

# This makes your Products show up
admin.site.register(Product)