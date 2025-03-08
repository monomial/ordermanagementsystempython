from tortoise import Model, fields
from datetime import datetime, timezone

class Customer(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=50, null=True)
    address = fields.CharField(max_length=255, null=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationship with orders
    orders = fields.ReverseRelation["Order"]

class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    price = fields.FloatField()
    sku = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationship with inventory
    inventory = fields.OneToOneRelation["Inventory"]
    
    # Add relation to order items
    order_items = fields.ReverseRelation["OrderItem"]

class Order(Model):
    id = fields.IntField(pk=True)
    customer = fields.ForeignKeyField("models.Customer", related_name="orders")
    order_date = fields.DatetimeField(default=datetime.now(timezone.utc))
    status = fields.CharField(max_length=50, default="pending")  # pending, completed, cancelled
    total_amount = fields.FloatField(default=0.0)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)

    # Add relation to order items
    items = fields.ReverseRelation["OrderItem"]

class OrderItem(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField("models.Order", related_name="items")
    product = fields.ForeignKeyField("models.Product", related_name="order_items")
    quantity = fields.IntField(default=1)
    unit_price = fields.FloatField()  # Price at time of purchase
    subtotal = fields.FloatField()  # unit_price * quantity
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "order_items"

class Inventory(Model):
    id = fields.IntField(pk=True)
    product = fields.OneToOneField("models.Product", related_name="inventory")
    quantity = fields.IntField(default=0)
    last_restock_date = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)
