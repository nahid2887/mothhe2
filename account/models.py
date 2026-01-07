from django.db import models
from django.utils import timezone

# Create your models here.

class LoanApplication(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    property_zip_code = models.CharField(max_length=10)
    property_address = models.TextField()
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    down_payment = models.DecimalField(max_digits=10, decimal_places=2)
    loan_purpose = models.CharField(
        max_length=20,
        choices=[('Purchase', 'Purchase'), ('Refinance', 'Refinance'), ('HELOC', 'HELOC')]
    )
    cash_out_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Store unique tokens for each loan application
    plaid_link_token = models.CharField(max_length=255, null=True, blank=True)
    plaid_public_token = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Loan Application by {self.full_name}"


class PlaidConnection(models.Model):
    """Simple model to store Plaid connection temporarily"""
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    item_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Plaid Connection for {self.loan_application.full_name}"






# from django.db import models
# from django.contrib.auth.models import User

# class PlaidAccount(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     access_token = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - Plaid Account"