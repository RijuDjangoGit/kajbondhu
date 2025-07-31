import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Services(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    is_authenticated = models.BooleanField(default=False)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    latitute = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    services = models.ManyToManyField(Services, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['user__username']

class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}"
    
    class Meta:
        verbose_name = 'User Rating'
        verbose_name_plural = 'User Ratings'
        ordering = ['-created_at']

class PaymentModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserOrderDetails(models.Model):
    order_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_user = models.ForeignKey(User, related_name='booking_user', on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    selected_payment = models.ForeignKey(PaymentModel, on_delete=models.CASCADE)
    order_details = models.TextField(blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    order_for_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.status})"
    
    class Meta:
        verbose_name = 'User Order Detail'
        verbose_name_plural = 'User Order Details'
        ordering = ['-order_date']

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(UserOrderDetails, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.order.user.username} - {self.status} at {self.changed_at}"
    
    class Meta:
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-changed_at']

class OrderPaymentDetails(models.Model):
    order = models.ForeignKey(UserOrderDetails, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.order.user.username} - {self.payment_method} ({self.payment_status})"
    
    class Meta:
        verbose_name = 'Order Payment Detail'
        verbose_name_plural = 'Order Payment Details'
        ordering = ['-payment_date']

class UserFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        verbose_name = 'User Feed'
        verbose_name_plural = 'User Feeds'
        ordering = ['-created_at']

class FeedImages(models.Model):
    feed = models.ForeignKey(UserFeed, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='feed_images/')

    def __str__(self):
        return f"Image for {self.feed.user.username} feed"
    
    class Meta:
        verbose_name = 'Feed Image'
        verbose_name_plural = 'Feed Images'
        ordering = ['-feed__created_at']

