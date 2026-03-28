# LLM Challenge - RAG Chat API

This project implements a RAG (Retrieval-Augmented Generation) Chat API using FastAPI, designed to provide a robust and scalable backend for conversational AI applications. It includes user authentication, database integration with PostgreSQL, and a structured project layout.

## Features

-   **FastAPI Backend**: High-performance Python web framework.
-   **User Authentication**: Secure user management with JWT.
-   **PostgreSQL Database**: Persistent storage for user data, conversations, and documents.
-   **Document Ingestion**: Upload documents, extract text, chunk content, and store metadata.
-   **Vector Retrieval**: Semantic search powered by Qdrant and `all-MiniLM-L6-v2` embeddings.
-   **RAG Chat UI**: Streamlit interface for upload, retrieval inspection, and grounded question answering.
-   **Docker & Docker Compose**: Containerized development and deployment for easy setup.
-   **Alembic Migrations**: Database schema management.
-   **Structured Project Layout**: Clear separation of concerns (API, services, repository, models, schemas, core).
-   **CORS Middleware**: Configured for flexible frontend integration.
-   **Request Logging**: Middleware for logging incoming requests and outgoing responses.

## Setup and Installation

### Prerequisites

-   Docker and Docker Compose (for containerized development)
-   Python 3.13+
-   `uv` (for local development)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hariz723/llm-challenge.git
    cd llm-challenge
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory by copying `.env.example` and filling in the values.

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file:
   
3.  **Setup Project (Local Development):**
    To set up the Python virtual environment and install dependencies locally:
    ```bash
    make setup
    ```

4.  **Run Database Migrations:**
    If running locally, ensure your PostgreSQL database is accessible and then apply migrations:
    ```bash
    make migrate
    ```
    If using Docker Compose, run migrations inside the `ragapp` container after starting it:
    ```bash
    make dev-run # Start Docker Compose services
    ```
    ```bash
    make migrate # apply migration
    ```
    ```bash
    make logs # for application logs
    ```
## Usage

### Running the Application

#### Local Development

To run the FastAPI application locally with auto-reload:
```bash
make run
```
The application will be available at `http://localhost:8000`.

#### Docker Compose

To build and run the application using Docker Compose:
```bash
make dev-run
```
The application will be available at `http://localhost:8000`.

To stop the Docker Compose services:
```bash
make dev-stop
```

To stop and remove Docker Compose containers:
```bash
make dev-down
```

## API Endpoints

The API documentation (Swagger UI) will be available at `http://localhost:8000/docs` after the application is running.

### Authentication

-   `/auth/api/register`: Register a new user.
-   `/auth/api/login`: Authenticate and get an access token.
-   `/auth/api/me`: Retrieve the current user.

### Other Endpoints

-   `/`: Basic health check.
-   `/documents/api/upload`: Upload and index a document.
-   `/documents/api/search`: Inspect retrieved chunks for a query.
-   `/documents/api/chat`: Ask a grounded question over indexed documents.

## Notes

-   If `LLM_API_URL` and `LLM_MODEL` are configured, the app will use that chat-completions-compatible endpoint to synthesize answers from retrieved context.
-   If those variables are omitted, the app still works with extractive fallback answers based on the top retrieved chunks.

## Development

### Linting and Formatting

This project uses `ruff` for linting and `black` for formatting.
You can run them with the following `make` commands:

```bash
make format
```

### Building Docker Images

To build Docker images without cache:
```bash
make dev-build
```

### Viewing Logs

To tail logs from Docker containers:
```bash
make dev-logs
```

## Contributing

Feel free to fork the repository, open issues, and submit pull requests.
