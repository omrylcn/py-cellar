from locust import HttpUser, task, between
import random

class UserDeviceDataBehavior(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks

    @task(2)  # Higher weight, more frequent execution
    def create_device_data(self):
        # Replace with the actual payload and endpoint
        self.client.post("/api/v1/user-device-data/", json={
            "user_id": int(random.randint(1,5)),  # Example user ID
            "device_unique_id": str(1),  # Example device ID
            "data": float(random.randint(0, 100)),
            "created_user": "admin"
            # Add other required fields
        })

    # @task(1)
    # def read_device_data(self):
    #     # Adjust the URL as necessary
    #     self.client.get("/api/v1/user-device-data/")

# Configure host and any authentication headers needed for your API in the class definition if necessary
