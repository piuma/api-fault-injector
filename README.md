# API Fault Injector

API Fault Injector is a tool designed to simulate various types of faults and errors in API responses. This can be useful for testing the robustness and error-handling capabilities of client applications.

## Features

- Simulate different HTTP status codes (e.g., 404 Not Found, 500 Internal Server Error)
- Inject delays to simulate network latency
- Return malformed JSON responses
- Throttle requests to simulate rate limiting
- Track and report activity summary

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/piuma/api-fault-injector.git
    cd api-fault-injector
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the API Fault Injector:
    ```sh
    python api-fault-injector.py
    ```

2. Configure the fault injection parameters using command-line arguments:
    - `--failure-rate`: Specify the rate at which to inject failures (0-1).
    - `--failure-status-code`: Specify the status code to return for failed requests (400-599).
    - `--throttle-rate`: Specify the rate at which to throttle requests (0-1).
    - `--throttle-delay`: Specify the delay in seconds for throttled requests.
    - `--rate-limit`: Specify the maximum number of requests per client within the rate limit window.
    - `--rate-limit-window`: Specify the rate limit window in seconds.
    - `--json-malformed`: Specify whether to return malformed JSON responses.

    Example:
    ```sh
    python api-fault-injector.py --failure-rate 0.1 --failure-status-code 500 --throttle-rate 0.2
    ```

## API Endpoints

The API Fault Injector includes a test backend application that accepts any URL and responds with a JSON payload. Here are some examples:

- **GET /**: Returns a sample JSON response.
- **POST /**: Updates the sample JSON response with the provided data.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the GNU General Public License (GPL).
