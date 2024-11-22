import random
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

import proxy
from proxy.common.flag import flags
from proxy.common.utils import build_http_response
from proxy.http.parser import HttpParser
from proxy.http.proxy import HttpProxyBasePlugin

# Track requests per client
request_counts = defaultdict(list)
# Track activity summary
activity_summary = {
    "total_requests": 0,
    "failed_requests": 0,
    "throttled_requests": 0,
    "rate_limited_requests": 0,
}

# See adblock.json file in repository for sample example config
flags.add_argument(
    "--failure-rate",
    type=float,
    default=0,
    help="Default: 0.0; Specify the rate at which to inject failures (0-1).",
)

flags.add_argument(
    "--failure-status-code",
    type=int,
    default=500,
    help="Default: 500; Specify the status code to return for failed requests (400-599).",
)

flags.add_argument(
    "--throttle-rate",
    type=float,
    default=0,
    help="Default: 0.0; Specify the rate at which to throttle requests (0-1).",
)

flags.add_argument(
    "--throttle-delay",
    type=int,
    default=0,
    help="Default: 0; Specify the delay in seconds for throttled requests.",
)

flags.add_argument(
    "--rate-limit",
    type=int,
    default=None,
    help="Default: None; Specify the maximum number of requests per client within the rate limit window.",
)

flags.add_argument(
    "--rate-limit-window",
    type=int,
    default=60,
    help="Default: 60; Specify the rate limit window in seconds.",
)

flags.add_argument(
    "--json-malformed",
    type=bool,
    default=False,
    help="Default: False; Specify whether to return malformed JSON responses.",
)


class ApiFaultInjectorPlugin(HttpProxyBasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters: List[Dict[str, Any]] = []

        # self.filters: List[Dict[str, Any]] = []
        if self.flags.failure_rate is not None:
            print("failure_rate", self.flags.failure_rate)

    def _apply_rate_limit(self, request: HttpParser, request_counts) -> HttpParser:
        client_ip = self.client.addr[0]
        if len(request_counts[client_ip]) >= self.flags.rate_limit:
            response = build_http_response(
                429,  # HTTP status code for Too Many Requests
                reason=b"Rate limit exceeded",
                headers={b"Content-Type": b"text/plain"},
            )

            print(f"Rate limit exceeded for {client_ip}")
            activity_summary["rate_limited_requests"] += 1
            self.client.queue(response)
            return None

        # Record the new request
        request_counts[client_ip].append(datetime.now())
        return request

    def _apply_failure_rate(self, request: HttpParser) -> HttpParser:

        if random.SystemRandom().random() < self.flags.failure_rate:

            reason = {
                400: b"Bad Request",
                401: b"Unauthorized",
                403: b"Forbidden",
                404: b"Not Found",
                405: b"Method Not Allowed",
                406: b"Not Acceptable",
                407: b"Proxy Authentication Required",
                408: b"Request Timeout",
                409: b"Conflict",
                410: b"Gone",
                411: b"Length Required",
                412: b"Precondition Failed",
                413: b"Payload Too Large",
                414: b"URI Too Long",
                415: b"Unsupported Media Type",
                416: b"Range Not Satisfiable",
                417: b"Expectation Failed",
                418: b"I'm a teapot",
                421: b"Misdirected Request",
                422: b"Unprocessable Entity",
                423: b"Locked",
                424: b"Failed Dependency",
                425: b"Too Early",
                426: b"Upgrade Required",
                428: b"Precondition Required",
                429: b"Too Many Requests",
                431: b"Request Header Fields Too Large",
                451: b"Unavailable For Legal Reasons",
                500: b"Internal Server Error",
                501: b"Not Implemented",
                502: b"Bad Gateway",
                503: b"Service Unavailable",
                504: b"Gateway Timeout",
                505: b"HTTP Version Not Supported",
                506: b"Variant Also Negotiates",
                507: b"Insufficient Storage",
                508: b"Loop Detected",
                510: b"Not Extended",
                511: b"Network Authentication Required",
            }.get(self.flags.failure_status_code, b"Error")

            response = build_http_response(
                self.flags.failure_status_code,  # HTTP status code
                reason=reason,
                headers={b"Content-Type": b"text/plain"},
            )
            print(f"Simulated failure for {self.client.addr[0]}")
            activity_summary["failed_requests"] += 1
            self.client.queue(response)
            return None
        return request

    def _apply_throttle(self):
        # Simulate throttling based on self.throttle_rate

        if random.SystemRandom().random() < self.flags.throttle_rate:
            print(f"Simulating throttling for {self.client.addr[0]}")
            time.sleep(self.flags.throttle_delay)
            activity_summary["throttled_requests"] += 1

    def _apply_json_malformed(self):
        """
        Modifies the request to return a malformed JSON response.
        """
        # Create a malformed JSON response
        malformed_json = '{"message": "This is a malformed JSON response"'

        # Build the HTTP response with the malformed JSON
        response = build_http_response(
            status_code=200,
            reason=b"OK",
            headers={
                b"Content-Type": b"application/json",
                b"Content-Length": str(len(malformed_json)).encode("utf-8"),
            },
            body=malformed_json.encode("utf-8"),
        )

        # Send the response
        self.client.queue(response)

    def before_upstream_connection(self, request: HttpParser) -> HttpParser:
        print("function: before_upstream_connection")

        activity_summary["total_requests"] += 1

        if self.flags.throttle_rate is not None:
            self._apply_throttle()

        if self.flags.failure_rate is not None:
            request = self._apply_failure_rate(request)

        if request is not None and self.flags.rate_limit is not None:
            client_ip = self.client.addr[0]
            current_time = datetime.now()

            # Clean up old requests
            request_counts[client_ip] = [
                timestamp
                for timestamp in request_counts[client_ip]
                if timestamp
                > current_time - timedelta(seconds=self.flags.rate_limit_window)
            ]

            request = self._apply_rate_limit(request, request_counts)

        if request is not None and self.flags.json_malformed is True:
            self._apply_json_malformed()
            request = None

        return request

    def handle_client_request(self, request: HttpParser) -> HttpParser:
        print("function: handle_client_request")
        return self.before_upstream_connection(request)

    def on_client_connection_close(self) -> None:
        # Print activity summary report
        print("\nActivity Summary Report:")
        print(f"Total Requests: {activity_summary['total_requests']}")
        print(f"Failed Requests: {activity_summary['failed_requests']}")
        print(f"Throttled Requests: {activity_summary['throttled_requests']}")
        print(f"Rate Limited Requests: {activity_summary['rate_limited_requests']}")


if __name__ == "__main__":
    proxy.main(plugins=["ApiFaultInjectorPlugin"])
