from locust import HttpUser, task, between

class UserDeviceDataBehavior(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks

    @task(2)  # Higher weight, more frequent execution
    def create_device_data(self):
        # Replace with the actual payload and endpoint
        self.client.post("/api/v1/user_device_data/", json={
            "user_id": 1,  # Example user ID
            "device_id": "1",
            "data": 42.0,
            "created_user": "admin"
            # Add other required fields
        })

    # @task(1)
    # def read_device_data(self):
    #     # Adjust the URL as necessary
    #     self.client.get("/api/v1/user-device-data/")

# Configure host and any authentication headers needed for your API in the class definition if necessary
