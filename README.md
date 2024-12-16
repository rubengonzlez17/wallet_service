# Wallets API

Wallets API is a Django-based application designed to manage wallet transactions, including recharges and charges between users and businesses. This API enables users to interact with their wallets, process transactions, and view transaction history.

---

## Installing

Install Python requirements (ensure you are inside the repository):

    $ pip install -r requirements.txt

---

### Project Execution

To start the Django development server, use the following command:

    $ python manage.py runserver

To deploy with [Gunicorn](https://gunicorn.org/):

    $ gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 600 wallet_service.wsgi:application

---

### Running with Docker

To launch the application using Docker, first build the Docker image:

    $ docker build -t wallet-service .

Then, run the container:

    $ docker run -p 8000:8000 wallet-service

The application will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Docker Image

The Docker image for this project is automatically built and pushed to Docker Hub via GitHub Actions. You can pull the latest image using:

    $ docker pull your-dockerhub-username/wallet-service:latest

Replace `your-dockerhub-username` with your actual Docker Hub username. The image tags are managed automatically, and you can also pull a specific version:

    $ docker pull your-dockerhub-username/wallet-service:<tag>

---

### Testing

To run tests, execute the following command:

    $ pytest

---

### Documentation

Swagger documentation for the API can be found by default at [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/), or through the Django REST framework UI at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) after logging in.

---

### Linter

To run the Python linter using flake8, first install flake8 if you don't have it:

    $ pip install flake8

Then, run flake8 on your project:

    $ flake8 .

---

### Continuous Integration and Deployment

This project uses GitHub Actions for continuous integration and deployment.

---

## API Endpoints

### Authentication

- **POST /api/token/**: Generate a token for user authentication.
  - Request body: 
    ```json
    {
      "username": "user_name",
      "password": "password"
    }
    ```

- **POST /api/auth/**: Authenticate users using their token. Token must be included in the headers as `Authorization: Token <your-token>`.

### Wallet Management

- **POST /api/wallets/create/**: Create a new wallet for a user. 
  - Request body:
    ```json
    {
      "balance": 1000.0
    }
    ```
  - Authentication is required.

- **GET /api/wallets/status/**: Retrieve the status of all wallets associated with the authenticated user.

### Transactions

- **POST /api/transactions/create/**: Create a new transaction (either "RECHARGE" or "CHARGE").
  - Request body:
    ```json
    {
      "wallet": "wallet-token",
      "transaction_type": "RECHARGE",
      "amount": 50.0
    }
    ```

- **GET /api/transactions/**: Retrieve a list of transactions for a specific wallet or all wallets.
  - Query parameters: 
    - `wallet` (optional): filter transactions by wallet token.

### Error Handling

The API returns appropriate error responses for invalid input, unauthorized access, or other failed actions.

---

### Notes on Transactions

- The transaction types are "RECHARGE" and "CHARGE". For "CHARGE" transactions, two transactions are created—one for the user's wallet and another for the merchant's wallet.
- The system ensures that charge transactions only proceed if the user has enough balance and if the merchant's wallet exists.

---

## Code Coverage

You can view the code coverage for this application at the following link:

[Wallet Service Coverage](https://rubengonzlez17.github.io/wallet_service/)

