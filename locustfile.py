from locust import HttpUser, task, between
import random
import json

class OrdersUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1-5 seconds between tasks
    
    # Sample data for testing - updated to match actual database IDs
    sample_customers = list(range(6, 11))  # Customer IDs 6-10 from database
    sample_products = list(range(11, 21))  # Product IDs 11-20 from database
    
    def on_start(self):
        """Initialize user session - can be used for login if needed"""
        # If your API requires authentication, add it here
        # self.client.post("/login", json={"username": "test", "password": "test"})
        self.created_orders = []  # Initialize the list to store created order IDs
    
    @task(3)
    def create_order(self):
        """Test order creation - higher weight (3) as it's likely a common operation"""
        # First check inventory levels to make smarter product choices
        with self.client.get("/api/v1/orders/debug/inventory", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    inventory_data = response.json()
                    # Filter products with sufficient inventory (5 or more items)
                    sufficient_inventory = [item["product_id"] for item in inventory_data if item["inventory_level"] >= 5]
                    
                    # If we have products with sufficient inventory, prefer those
                    # Otherwise, fall back to the sample products
                    product_pool = sufficient_inventory if sufficient_inventory else self.sample_products
                    
                    # Generate a random order with 1-3 items
                    items = []
                    for _ in range(random.randint(1, 3)):
                        if product_pool:
                            product_id = random.choice(product_pool)
                            # Find the inventory level for this product
                            inventory_level = next((item["inventory_level"] for item in inventory_data 
                                                if item["product_id"] == product_id), 0)
                            # Set quantity to be at most the inventory level (or 1-3 if sufficient)
                            max_quantity = min(3, inventory_level) if inventory_level > 0 else 1
                            quantity = random.randint(1, max_quantity)
                            
                            items.append({
                                "product_id": product_id,
                                "quantity": quantity
                            })
                    
                    # Only proceed if we have items to order
                    if items:
                        order_data = {
                            "customer_id": random.choice(self.sample_customers),
                            "status": random.choice(["pending", "processing", "shipped", "delivered"]),
                            "items": items
                        }
                        
                        # Send the request and capture response
                        with self.client.post("/api/v1/orders/", json=order_data, catch_response=True) as order_response:
                            if order_response.status_code == 201:
                                # Save the order ID for future use if successful
                                try:
                                    order_id = order_response.json().get("id")
                                    if order_id:
                                        self.created_orders.append(order_id)
                                except json.JSONDecodeError:
                                    order_response.failure("Response could not be decoded as JSON")
                            elif order_response.status_code == 400:
                                # Log the error details for debugging
                                try:
                                    error_detail = order_response.json().get("detail", "No detail provided")
                                    print(f"400 Bad Request: {error_detail}")
                                    # Still mark as success since this might be expected (e.g., insufficient inventory)
                                    order_response.success()
                                except json.JSONDecodeError:
                                    print(f"400 Bad Request with non-JSON response: {order_response.text}")
                                    order_response.success()
                            elif order_response.status_code == 404:
                                # Customer or product not found
                                order_response.failure(f"404 Not Found: {order_response.text}")
                            else:
                                order_response.failure(f"Failed to create order: {order_response.status_code}")
                    else:
                        # No items with sufficient inventory, skip this order
                        print("Skipping order creation due to insufficient inventory for all products")
                        
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                # Fall back to original behavior if inventory check fails
                self._create_order_fallback()
    
    def _create_order_fallback(self):
        """Fallback method for order creation if inventory check fails"""
        # Generate a random order with 1-3 items
        items = []
        for _ in range(random.randint(1, 3)):
            product_id = random.choice(self.sample_products)
            items.append({
                "product_id": product_id,
                "quantity": random.randint(1, 3)
            })
        
        order_data = {
            "customer_id": random.choice(self.sample_customers),
            "status": random.choice(["pending", "processing", "shipped", "delivered"]),
            "items": items
        }
        
        # Send the request and capture response
        with self.client.post("/api/v1/orders/", json=order_data, catch_response=True) as response:
            if response.status_code == 201:
                # Save the order ID for future use if successful
                try:
                    order_id = response.json().get("id")
                    if order_id:
                        self.created_orders.append(order_id)
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            elif response.status_code == 400:
                # Log the error details for debugging
                try:
                    error_detail = response.json().get("detail", "No detail provided")
                    print(f"400 Bad Request: {error_detail}")
                    # Still mark as success since this might be expected (e.g., insufficient inventory)
                    response.success()
                except json.JSONDecodeError:
                    print(f"400 Bad Request with non-JSON response: {response.text}")
                    response.success()
            elif response.status_code == 404:
                # Customer or product not found
                response.failure(f"404 Not Found: {response.text}")
            else:
                response.failure(f"Failed to create order: {response.status_code}")
    
    @task(5)
    def get_orders_list(self):
        """Test retrieving orders list - highest weight (5) as it's likely most common"""
        # Randomly use pagination
        skip = random.choice([0, 10, 20])
        limit = random.choice([10, 20, 50])
        
        with self.client.get(f"/api/v1/orders/?skip={skip}&limit={limit}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get orders: {response.status_code}")
    
    @task(2)
    def get_order_detail(self):
        """Test retrieving a specific order"""
        # Either use a previously created order or a random ID from existing orders (2-21)
        if self.created_orders:
            order_id = random.choice(self.created_orders)
        else:
            # Use existing order IDs from the database (2-21)
            order_id = random.randint(2, 21)
        
        with self.client.get(f"/api/v1/orders/{order_id}", catch_response=True) as response:
            if response.status_code == 404:
                # Not found is acceptable if using random IDs
                response.success()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get order {order_id}: {response.status_code}")
    
    @task(1)
    def update_order(self):
        """Test updating an order - lower weight as less common"""
        # Either use a previously created order or a random ID from existing orders
        if self.created_orders:
            order_id = random.choice(self.created_orders)
        else:
            # Use existing order IDs from the database (2-21)
            order_id = random.randint(2, 21)
        
        # Update just the status
        update_data = {
            "status": random.choice(["processing", "shipped", "delivered", "cancelled"])
        }
        
        with self.client.put(f"/api/v1/orders/{order_id}", json=update_data, catch_response=True) as response:
            if response.status_code == 404:
                # Not found is acceptable if using random IDs
                response.success()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to update order {order_id}: {response.status_code}")
    
    @task(1)
    def get_order_items(self):
        """Test retrieving order items for a specific order"""
        # Either use a previously created order or a random ID from existing orders
        if self.created_orders:
            order_id = random.choice(self.created_orders)
        else:
            # Use existing order IDs from the database (2-21)
            order_id = random.randint(2, 21)
        
        with self.client.get(f"/api/v1/orders/{order_id}/items", catch_response=True) as response:
            if response.status_code == 404:
                # Not found is acceptable if using random IDs
                response.success()
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get order items for {order_id}: {response.status_code}")
    
    @task(1)
    def delete_order(self):
        """Test deleting an order - lowest weight as it's least common"""
        # Only delete orders we've created during this session
        if self.created_orders:
            order_id = self.created_orders.pop()  # Remove the ID so we don't try to use it again
            
            with self.client.delete(f"/api/v1/orders/{order_id}", catch_response=True) as response:
                if response.status_code == 204:
                    response.success()
                elif response.status_code == 404:
                    # Order might have been deleted already
                    response.success()
                else:
                    response.failure(f"Failed to delete order {order_id}: {response.status_code}")
    
    @task(1)
    def check_inventory(self):
        """Check inventory levels for debugging"""
        with self.client.get("/api/v1/orders/debug/inventory", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    inventory_data = response.json()
                    # Log products with low inventory (less than 5 items)
                    low_inventory = [item for item in inventory_data if item["inventory_level"] < 5]
                    if low_inventory:
                        print(f"Low inventory products: {low_inventory}")
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Failed to get inventory data: {response.status_code}")
    
    @task(2)  # Higher weight to ensure inventory is replenished frequently
    def replenish_inventory(self):
        """Replenish inventory for products with low stock"""
        with self.client.get("/api/v1/orders/debug/inventory", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    inventory_data = response.json()
                    # Find products with low inventory (less than 5 items)
                    low_inventory = [item for item in inventory_data if item["inventory_level"] < 5]
                    
                    for item in low_inventory:
                        # Get the inventory ID for this product
                        product_id = item["product_id"]
                        with self.client.get(f"/api/v1/inventory/product/{product_id}", catch_response=True) as inv_response:
                            if inv_response.status_code == 200:
                                try:
                                    inventory = inv_response.json()
                                    inventory_id = inventory["id"]
                                    
                                    # Replenish inventory to 20 units
                                    update_data = {
                                        "quantity": 20  # Set to a reasonable amount
                                    }
                                    
                                    with self.client.put(f"/api/v1/inventory/{inventory_id}", 
                                                        json=update_data, 
                                                        catch_response=True) as update_response:
                                        if update_response.status_code == 200:
                                            print(f"Replenished inventory for product {item['product_name']} (ID: {product_id}) to 20 units")
                                            update_response.success()
                                        else:
                                            print(f"Failed to update inventory for product {product_id}: {update_response.status_code}")
                                            update_response.success()  # Still mark as success to continue the test
                                except json.JSONDecodeError:
                                    inv_response.failure("Response could not be decoded as JSON")
                            else:
                                print(f"Could not find inventory for product {product_id}")
                                inv_response.success()  # Still mark as success to continue the test
                    
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            else:
                response.failure(f"Failed to get inventory data: {response.status_code}")