from django.contrib import admin
from .models import (
    UserRole, Services, UserProfile, UserRating, PaymentModel,
    UserOrderDetails, OrderStatusHistory, OrderPaymentDetails,
    UserFeed, FeedImages
)

# Inline for FeedImages to be used in UserFeed admin
class FeedImagesInline(admin.TabularInline):
    model = FeedImages
    extra = 1
    readonly_fields = ('image',)

# Inline for OrderStatusHistory to be used in UserOrderDetails admin
class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'changed_at', 'changed_by')
    can_delete = False

# Inline for OrderPaymentDetails to be used in UserOrderDetails admin
class OrderPaymentDetailsInline(admin.TabularInline):
    model = OrderPaymentDetails
    extra = 0
    readonly_fields = ('payment_method', 'payment_status', 'payment_date', 'transaction_id', 'amount', 'payment_details')
    can_delete = False

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ('name',)

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ('name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'is_authenticated', 'rating', 'location')
    search_fields = ('user__username', 'full_name', 'phone_number', 'location')
    list_filter = ('role', 'is_authenticated', 'location')
    list_editable = ('is_authenticated', 'role')
    raw_id_fields = ('user',)
    readonly_fields = ('rating',)
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'role', 'is_authenticated')
        }),
        ('Personal Details', {
            'fields': ('phone_number', 'bio', 'profile_picture', 'date_of_birth', 'location')
        }),
        ('Professional Details', {
            'fields': ('website', 'services', 'rating', 'latitute', 'longitude')
        }),
    )

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at', 'comment')
    search_fields = ('user__username', 'comment')
    list_filter = ('rating', 'created_at')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ('name',)

@admin.register(UserOrderDetails)
class UserOrderDetailsAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'booking_user', 'service', 'status', 'order_date', 'order_for_date')
    search_fields = ('order_id', 'user__username', 'booking_user__username', 'service__name')
    list_filter = ('status', 'order_date', 'order_for_date', 'service')
    raw_id_fields = ('user', 'booking_user', 'service', 'selected_payment')
    readonly_fields = ('order_id', 'order_date')
    inlines = [OrderStatusHistoryInline, OrderPaymentDetailsInline]
    list_editable = ('status',)
    date_hierarchy = 'order_date'
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'booking_user', 'service', 'selected_payment', 'status')
        }),
        ('Details', {
            'fields': ('order_details', 'order_date', 'order_for_date')
        }),
    )

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_at', 'changed_by')
    search_fields = ('order__order_id', 'changed_by__username')
    list_filter = ('status', 'changed_at')
    raw_id_fields = ('order', 'changed_by')
    readonly_fields = ('changed_at',)
    date_hierarchy = 'changed_at'

@admin.register(OrderPaymentDetails)
class OrderPaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'payment_status', 'amount', 'payment_date')
    search_fields = ('order__order_id', 'transaction_id', 'payment_method')
    list_filter = ('payment_status', 'payment_date', 'payment_method')
    raw_id_fields = ('order',)
    readonly_fields = ('payment_date', 'transaction_id')
    date_hierarchy = 'payment_date'

@admin.register(UserFeed)
class UserFeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'created_at')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    inlines = [FeedImagesInline]
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(FeedImages)
class FeedImagesAdmin(admin.ModelAdmin):
    list_display = ('feed', 'image')
    search_fields = ('feed__user__username',)
    list_filter = ('feed__created_at',)
    raw_id_fields = ('feed',)