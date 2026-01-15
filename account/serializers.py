from rest_framework import serializers
from .models import LoanApplication, PlaidConnection


class ContactSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=60, required=False)
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(style={'base_template': 'textarea.html'})


class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'


class PlaidLinkSerializer(serializers.Serializer):
    public_token = serializers.CharField()
    loan_application_id = serializers.IntegerField()