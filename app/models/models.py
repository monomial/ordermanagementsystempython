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
    orders = fields.ManyToManyRelation["Order"]

class Order(Model):
    id = fields.IntField(pk=True)
    customer = fields.ForeignKeyField("models.Customer", related_name="orders")
    order_date = fields.DatetimeField(default=datetime.now(timezone.utc))
    status = fields.CharField(max_length=50, default="pending")  # pending, completed, cancelled
    total_amount = fields.FloatField(default=0.0)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationship with products through association table
    products = fields.ManyToManyRelation["Product"]

class Inventory(Model):
    id = fields.IntField(pk=True)
    product = fields.OneToOneField("models.Product", related_name="inventory")
    quantity = fields.IntField(default=0)
    last_restock_date = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)
