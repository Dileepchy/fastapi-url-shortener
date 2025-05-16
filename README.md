# 12-Factor FastAPI URL Shortener

This is a simple URL shortening service built with FastAPI, designed to demonstrate the application of the 12-Factor App principles.

It accepts a long URL, generates a short code, and stores the mapping. Requests to the short code URL are redirected to the original long URL.

**Note:** For simplicity in this assignment, the URL mapping is stored in **in-memory storage**. This is a deliberate simplification and a point of discussion regarding how it violates certain 12-Factor principles (as explained below) and how a production application would externalize state using a backing service like Redis or a database.

## 12-Factor Principles Applied

Here's how this project addresses each of the 12 factors:

1.  **Codebase:**

    - The application is tracked in a single codebase using Git.
    - It is designed to be deployed multiple times (e.g., development, staging, production) from this single codebase.
    - **In this project:** Hosted in a single GitHub repository.

2.  **Dependencies:**

    - Dependencies are explicitly declared using `requirements.txt`.
    - Dependencies are isolated using Python virtual environments (or implicitly via Docker).
    - **In this project:** `requirements.txt` lists FastAPI, Uvicorn, pydantic-settings, shortuuid, and testing dependencies.

3.  **Config:**

    - Configuration is stored in the environment, separate from the code.
    - Environment variables are used to configure the application (e.g., listening port).
    - `pydantic-settings` is used to easily load environment variables with type validation and default values.
    - `.env.example` provides documentation and examples for local development configuration but is NOT committed as `.env`.
    - **In this project:** `APP_PORT` is read from environment variables using `pydantic-settings`.

4.  **Backing Services:**

    - Backing services (like databases, message queues, cache stores) are treated as attached resources, typically connected via configuration (URIs, credentials) from the environment.
    - **In this project:** The current in-memory storage _violates_ this principle as the state is coupled to the process. The README explains this limitation and how replacing the in-memory dictionary with a connection to an external Redis or PostgreSQL database (configured via environment variables like `REDIS_URL` or `DATABASE_URL`) would align with this principle.

5.  **Build, Release, Run:**

    - Strictly separate the build, release, and run stages.
    - The build stage transforms the code into an executable bundle.
    - The release stage combines the build with configuration.
    - The run stage runs the release.
    - **In this project:** A `Dockerfile` defines the build process (takes code and dependencies, creates image). Running the Docker image with specific environment variables constitutes the release (image + config) and run stages.

6.  **Processes:**

    - Execute the application as one or more stateless processes. Any necessary state should be externalized to a backing service.
    - **In this project:** The use of an in-memory dictionary for URL storage means the _processes_ are _not_ truly stateless, as their state is tied to the process instance's memory. Scaling would lead to inconsistent state across instances. This violates the principle. The README explains that externalizing state (as discussed in Factor IV) is necessary for processes to be stateless and horizontally scalable. The API endpoints themselves (receiving requests, looking up/adding URLs) are designed to be stateless interactions with the store.

7.  **Port Binding:**

    - Export services via port binding. The web server process binds to a port and listens for requests.
    - **In this project:** Uvicorn, the ASGI server running the FastAPI app, binds to a port specified by the `APP_PORT` environment variable, making the service accessible.

8.  **Concurrency:**

    - Scale out via the process model. Add more processes (or threads/workers within a process, though processes are preferred for isolation) to handle increased load.
    - **In this project:** The `Dockerfile` is configured to run Uvicorn, which can be started with multiple workers (`uvicorn app.main:app --workers 4`) or scaled by running multiple Docker containers. This horizontal scaling relies on the assumption that the underlying state (the URL store) is handled externally and consistently (which is the discussed limitation of the current in-memory store).

9.  **Disposability:**

    - Maximize robustness with fast startup and graceful shutdown. Processes should be able to start and stop quickly.
    - **In this project:** FastAPI and Uvicorn are designed for fast startup. The simple in-memory state allows for quick shutdown without complex cleanup (though losing state is the side effect).

10. **Dev/Prod Parity:**

    - Keep development, staging, and production environments as similar as possible.
    - **In this project:** Using `requirements.txt` ensures the same dependencies are used everywhere. Running the app locally within a virtual environment or via Docker provides a similar environment to the production Docker container. Configuration is handled consistently via environment variables in all environments.

11. **Logs:**

    - Treat logs as event streams. Write logs to standard output (stdout) and standard error (stderr). The execution environment should handle capturing, aggregating, and storing logs.
    - **In this project:** The application uses Python's standard `logging` module and Uvicorn logs request/error information to stdout/stderr. The Docker container output can be captured by `docker logs` or orchestration platforms.

12. **Admin Processes:**
    - Run admin/management tasks as one-off processes. These are separate from the main long-running web processes.
    - **In this project:** This simple application doesn't have complex admin tasks. If it used a database (as discussed in Factor IV), database migrations would be an example of a one-off admin process run separately (e.g., `alembic upgrade head`).

## Prerequisites

- Git
- Python 3.8+
- Docker (for containerized setup)

## Getting Started (Local)

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Dileepchy/fastapi-url-shortener.git
    cd fastapi-url-shortener
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**

    - Copy the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Edit the `.env` file to set your desired configuration (e.g., `APP_PORT`).

5.  **Run the application:**

    ```bash
    uvicorn app.main:app --reload --env-file .env
    ```

    The `--reload` flag is useful for development. The `--env-file` flag loads variables from `.env` (alternatively, you can export variables directly in your shell).

6.  **Access the API:**
    - Open your browser to `http://localhost:8000/docs` (or the port you configured) to see the Swagger UI.
    - You can test the `/shorten` and `/{short_code}` endpoints from there.

## Getting Started (Docker)

1.  **Clone the repository:** (If you haven't already)

    ```bash
    git clone <Your GitHub Repo Link Here>
    cd fastapi-url-shortener
    ```

2.  **Configure environment variables:**

    - Ensure you have a `.env` file as created in the local setup step. This file will be passed to the Docker container.

3.  **Build the Docker image:**

    ```bash
    docker build -t my-url-shortener .
    ```

4.  **Run the Docker container:**

    ```bash
    docker run -d -p 8000:${APP_PORT:-8000} --env-file .env --name url-shortener-app my-url-shortener
    ```

    - `-d`: Run the container in detached mode.
    - `-p 8000:${APP_PORT:-8000}`: Map local port 8000 to the container's exposed port (read from `APP_PORT` in `.env`, defaulting to 8000).
    - `--env-file .env`: Load environment variables from your `.env` file into the container.
    - `--name url-shortener-app`: Assign a name to the container.

5.  **Access the API:**

    - Open your browser to `http://localhost:8000/docs` (or the port you mapped) to see the Swagger UI.
    - You can test the endpoints.

6.  **Stop and remove the container:**
    ```bash
    docker stop url-shortener-app
    docker rm url-shortener-app
    ```

## API Endpoints

- `POST /shorten`: Takes a JSON body with `{"long_url": "your_long_url_here"}` and returns a short code and the full short URL.
- `GET /{short_code}`: Redirects the client to the original long URL associated with the short code. Returns 404 if the code is not found.
- `GET /docs`: Swagger UI documentation.
- `GET /redoc`: ReDoc documentation.

## Configuration

The application is configured via environment variables, loaded using `pydantic-settings`.

- `APP_PORT`: The port the Uvicorn server will listen on inside the container/process (defaults to `8000`).

See `.env.example` for an example configuration file.

## Running Tests

Tests are located in the `tests/` directory and use `pytest`.

1.  Ensure you have installed dependencies (`pip install -r requirements.txt`).
2.  Run pytest from the project root:
    ```bash
    pytest
    ```

## CI Workflow

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs on pushes and pull requests to the `main` branch.

This workflow:

1.  Checks out the code.
2.  Sets up Python 3.9.
3.  Installs dependencies from `requirements.txt`.
4.  Runs the `pytest` tests.

You can see the results of the CI runs in the "Actions" tab of the GitHub repository.

[![CI Status](https://github.com/<Your_GitHub_Username>/<Your_Repo_Name>/actions/workflows/ci.yml/badge.svg)](https://github.com/<Your_GitHub_Username>/<Your_Repo_Name>/actions/workflows/ci.yml)
_(Replace `<Your_GitHub_Username>` and `<Your_Repo_Name>` with your actual GitHub details)_

## Screenshoots

The demonstrates:

- Running the application locally.
- Accessing the `/docs` (Swagger UI).
- Using the `/shorten` endpoint to create a short URL.
- Accessing the generated short URL to verify redirection.
- Building and running the application using Docker.
- Accessing the app via Docker.
- Showing a successful CI run on the GitHub Actions page.

---

Remember to replace the placeholder links and information in the `README.md` with your actual GitHub repository URL and video link. Good luck!
