from django.contrib import admin
from .models import LoanApplication

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email', 'phone_number', 'loan_purpose', 'annual_income', 'purchase_price', 'down_payment'
    )
    search_fields = ('full_name', 'email', 'phone_number', 'loan_purpose')
    list_filter = ('loan_purpose',)

# Register your models here.
