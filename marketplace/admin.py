from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models  # FIXED: Imported models so Case and When work properly
from .models import User, Product, Category, Order, PayoutRequest  # FIXED: Cleaned up duplicate imports

class CustomUserAdmin(UserAdmin):
    # Add wallet_balance to the columns you see when looking at all users
    list_display = ('username', 'email', 'is_vendor', 'store_name', 'wallet_balance')

    # This adds your new fields to the section in Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Celestial Profile', {'fields': ('image',)}),
        ('Store Details', {'fields': ('is_official_store', 'is_student_seller', 'store_name', 'wallet_balance')}),
    )

# Register the User model (Only ONCE here)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'product', 'total_price', 'status', 'momo_transaction_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('momo_transaction_id', 'buyer__username', 'product__title')
    list_editable = ('status',)
    actions = ['approve_payments']

    def approve_payments(self, request, queryset):
        for order in queryset:
            order.status = 'IN_ESCROW'
            order.generate_otp()
        self.message_user(request, "Selected orders have been moved to Escrow and OTPs generated.")

    approve_payments.short_description = "Approve MoMo Payment & Generate OTP"


# FIXED: Removed the duplicate User registration line that was sitting here


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'amount', 'momo_number', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('vendor__username', 'vendor__store_name', 'momo_number')
    # 4. INSTANT TOGGLE: Lets you change status from the main table list view and hit "Save"
    list_editable = ('status',)

        # 5. BULK ACTION: Lets you check boxes and mark multiple requests as Paid instantly
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone

            # Update status and log the exact timestamp you paid them
        updated_count = queryset.filter(status='PENDING').update(
            status='PAID',
            processed_at=timezone.now()
        )

        self.message_user(
            request,
            f"💰 Successfully marked {updated_count} payout request(s) as PAID and logged timestamps."
        )

    mark_as_paid.short_description = "Mark selected requests as PAID / Cleared"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by(
            models.Case(
                models.When(status='PENDING', then=0),
                default=1,
            ),
            '-requested_at'
        )
