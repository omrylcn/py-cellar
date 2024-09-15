# Advanced FastAPI CRUD API

This project is a robust, production-ready FastAPI application implementing a CRUD API with advanced features such as authentication, authorization, and comprehensive testing.

## Table of Contents

- [Advanced FastAPI CRUD API](#advanced-fastapi-crud-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Setup and Installation](#setup-and-installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
  - [API Documentation](#api-documentation)
  - [Testing](#testing)
  - [Deployment](#deployment)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- FastAPI-based CRUD operations
- Asynchronous SQLAlchemy with PostgreSQL
- JWT Authentication and Authorization
- Environment-based configuration management
- Comprehensive test suite with pytest
- Docker support for easy deployment
- Automatic API documentation with Swagger UI

## Project Structure

```
project_root/
├── api/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── user_data.py
│   │   └── users.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── user_data.py
│   │   └── users.py
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── routers.py
│   ├── schemas.py
│   └── secure.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_admin.py
│   │   ├── test_user_data.py
│   │   └── test_users.py
│   └── test_crud/
│       ├── __init__.py
│       ├── test_admin.py
│       ├── test_user_data.py
│       └── test_users.py
├── .env
├── .env.test
├── .gitignore
├── config.yaml
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Copy `.env.example` to `.env` and fill in your specific values
   - For testing, copy `.env.example` to `.env.test` and fill in test-specific values

5. Set up your database:
   - Ensure PostgreSQL is installed and running
   - Create databases for development and testing as specified in your `.env` and `.env.test` files

## Configuration

This project uses a hybrid configuration system combining `omegaconf` and `python-dotenv`:

- `config.yaml`: Contains public, non-sensitive configuration
- `.env`: Contains sensitive configuration for development
- `.env.test`: Contains sensitive configuration for testing

To add new configuration options:

1. Add public options to `config.yaml`
2. Add sensitive options to `.env` and `.env.test`
3. Update `api/config.py` to load and use the new options

## Running the Application

To run the application in development mode:

```
python main.py
```

For production, we recommend using a production-grade ASGI server like Uvicorn or Hypercorn:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, you can access the automatic API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

To run tests:

```
FASTAPI_ENV=test pytest tests/
```

This command sets the `FASTAPI_ENV` environment variable to `test`, ensuring that the test configuration is used.

To generate a coverage report:

```
FASTAPI_ENV=test pytest --cov=api tests/
```

## Deployment

This project includes a Dockerfile and docker-compose.yml for easy containerization and deployment.

To build and run with Docker:

```
docker-compose up --build
```

For production deployment, consider using a reverse proxy like Nginx and ensure all sensitive information is properly secured.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure you update tests as appropriate and adhere to the existing coding style.

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

Remember to keep your `.env` and `.env.test` files secure and never commit them to version control. Always use environment variables for sensitive information in production environments.

For any questions or issues, please open an issue in the GitHub repository.