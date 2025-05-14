from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.product_name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.quantity})"
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Linked to the user
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Add this field
    status = models.CharField(max_length=20, default="Pending")  # e.g., Pending, Paid, Shipped
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    

class Payment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='payments')  # Link payment to a user
    razorpay_order_id = models.CharField(max_length=100, unique=True)  # Store Razorpay order ID
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)  # Payment ID received after successful payment
    amount = models.IntegerField()  # Amount in paise
    status = models.CharField(max_length=50, choices=[  # Status of the payment
        ('created', 'Created'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ], default='created')
    created_at = models.DateTimeField(default=now)  # Timestamp for when the payment was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update

    def __str__(self):
        return f"Payment {self.razorpay_order_id} ({self.status})"

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Allows smooth migration
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(auto_now_add=True)  # ✅ More precise timestamps

    def __str__(self):
        return f"Order #{self.order.id if self.order else 'Unassigned'} - {self.update_desc[:50]}"