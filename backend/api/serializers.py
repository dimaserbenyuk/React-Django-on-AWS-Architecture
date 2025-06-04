from rest_framework import serializers
from .models import Customer, Invoice, InvoiceItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['name', 'quantity', 'unit_price']


class InvoiceSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'company_name', 'address', 'customer', 'items']

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Invoice must contain at least one item.")
        for item in items:
            if item.get("quantity", 0) <= 0:
                raise serializers.ValidationError("Item quantity must be greater than zero.")
            if item.get("unit_price", 0) < 0:
                raise serializers.ValidationError("Item unit price cannot be negative.")
        return items

    def create(self, validated_data):
        customer_data = validated_data.pop("customer")
        items_data = validated_data.pop("items")

        customer, _ = Customer.objects.get_or_create(**customer_data)
        invoice = Invoice.objects.create(customer=customer, **validated_data)

        for item in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item)

        return invoice
