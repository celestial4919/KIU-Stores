from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    image = CloudinaryField('image', null=True, blank=True)
    # This distinguishes your users
    is_vendor = models.BooleanField(default=False)
    is_student_seller = models.BooleanField(default=False)
    is_official_store = models.BooleanField(default=False)
    # Business Identity
    store_name = models.CharField(max_length=100, blank=True, null=True)
    business_specialty = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Laptops & IT Solutions")
    bio = models.TextField(max_length=500, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Main Campus, Room 12")
    working_hours = models.CharField(max_length=100, blank=True, null=True, default="Mon-Fri, 8AM - 6PM")
    # Technical Settings
    dark_mode = models.BooleanField(default=False)
    data_saver = models.BooleanField(default=False)
    is_invisible = models.BooleanField(default=False)
    
    # Professional Links
    portfolio_url = models.URLField(blank=True, null=True, help_text="Link to Instagram or Website")
    def __str__(self):
        return self.store_name if self.store_name else self.username
    
    # NEW: The Following System
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) # This is for the URL (e.g., 'electronics')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"        

from decimal import Decimal # Make sure this is at the top with other imports

# ... keep User, Category etc. where they are ...

class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Pricing fields
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = '/static/images/placeholder.png'
        return url

    def save(self, *args, **kwargs):
        # Store the original price if it's the first time saving
        if not self.original_price:
            self.original_price = self.price

        price_val = float(self.original_price)
        
        # YOUR PRICING LOGIC
        if price_val < 50000:
            markup = 1.10  # 10%
        elif price_val < 100000:
            markup = 1.08  # 8%
        elif price_val < 250000:
            markup = 1.07  # 7%
        else:
            markup = 1.06  # 6%

        # Update the final price with the markup
        self.price = Decimal(price_val * markup)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - USh {self.price:,.0f}"
    
    # ADD TO models.py
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('escrow', 'Held in Escrow'),
        ('completed', 'Funds Released'),
        ('cancelled', 'Cancelled/Refunded'),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True) # For Flutterwave/MTN
    
class CartItem(models.Model):
    # Links the item to a specific user (Bishop or any student)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    
    # Links to the product being bought
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Allows students to buy more than one of the same item
    quantity = models.PositiveIntegerField(default=1)
    
    # Tracks when they added it
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        # Multiply price by quantity for the final sum
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username}'s cart - {self.product.title}"

class Review(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField(default=5) # 1 to 5 stars
    comment = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_purchase = models.BooleanField(default=False) # True if they actually used the OTP code

    def __str__(self):
        return f"Review for {self.vendor.store_name} by {self.reviewer.username}"

from decimal import Decimal

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.name}"  

from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at') # Columns you see in the list
    list_filter = ('created_at',) # Filter by date on the right side
    search_fields = ('name', 'subject', 'message') # Search bar for messages
    readonly_fields = ('created_at',) # Prevents accidental editing of the timestamp             
    

class BusinessApplication(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    business_specialty = models.CharField(max_length=100, help_text="e.g., Fast Food, Electronics")
    physical_location = models.CharField(max_length=255, help_text="Where is your shop located?")
    
    # MERCHANT CODE: Crucial for easy money redirection (MTN/Airtel)
    merchant_code = models.CharField(max_length=50, help_text="Enter your Merchant or Till Number")
    
    application_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.business_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.title}"
    
class Message(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    # Inside your Message class in models.py

    def get_other_user(self, current_user):
        """Returns the person the current user is talking to."""
        return self.receiver if self.sender == current_user else self.sender
    
    @property
    def get_other_user_id(self):
    # If the current message sender is the one viewing it, return the receiver's ID
    # Otherwise, return the sender's ID
        return self.receiver.id # This is a simplified version for the template loop
    
class Report(models.Model):
    REPORT_CHOICES = [
        ('scam', 'Potential Scam'),
        ('prohibited', 'Prohibited/Illegal Item'),
        ('misleading', 'Misleading Information'),
        ('contact', 'Off-platform Transaction Request'),
        ('other', 'Other Issue'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_CHOICES)
    description = models.TextField(help_text="Provide more details about why you are reporting this.")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report: {self.reason} on {self.product.title}"
