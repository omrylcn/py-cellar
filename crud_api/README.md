# FastAPI PostgreSQL CRUD API Template

This is a template for creating a CRUD API using FastAPI and PostgreSQL. The API is designed to run independently, while PostgreSQL is containerized using Docker for easy setup and management.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- pip (Python package manager)

## Environment Setup

This project uses two environments: development (dev) and testing (test). Environment variables are managed using `.env` files.

1. Create two environment files in the root directory:
   - `.env.dev` for development
   - `.env.test` for testing

2. Add the following variables to both files, adjusting values as needed:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   SECRET_KEY=your_secret_key_for_jwt
   ```

   For the test environment, use a different database name to keep test data separate.

3. Environment Loading:
   - For development: The `.env.dev` file is loaded when running the API with `ENV=dev`.
   - For testing: The `.env.test` file is loaded automatically when running pytest.

   Example usage:
   ```bash
   ENV=dev python main.py  # Loads .env.dev
   pytest tests/ -v        # Automatically loads .env.test
   ```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Start PostgreSQL using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

To start the API server in development mode:

```bash
ENV=dev python main.py --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## Testing

To run the test suite:

```bash
pytest tests/ -v
```

This command automatically uses the test environment configuration from `.env.test`.

### Mock Data for Testing

The test suite includes mock data for authentication and API testing. Here's how it works:

1. A mock user is created in the test database when running the tests.
2. To get an authentication token, use the `/token` endpoint with the mock user credentials:
   ```
   username: testuser
   password: testpassword
   ```

3. Use the obtained token in the `Authorization` header for authenticated API requests:
   ```
   Authorization: Bearer <your_token_here>
   ```

Example of getting a token (using curl):
```bash
curl -X POST "http://localhost:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=testuser&password=testpassword"
```

## API Documentation

Once the server is running, you can view the auto-generated API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.