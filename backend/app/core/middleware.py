"""Security and rate limiting middleware."""

import time
from collections import defaultdict
from typing import Awaitable, Callable, Dict, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-ancestors 'none'"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter using token bucket algorithm.
    
    Limits:
    - Per API key: RATE_LIMIT requests per minute
    - Per IP: RATE_LIMIT requests per minute
    """

    def __init__(self, app, rate_limit: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = 60  # seconds
        
        # Token buckets: Dict[key, Tuple[tokens, last_refill]]
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(lambda: (rate_limit, time.time()))
        
        # Track upload/export endpoints
        self.expensive_endpoints = {
            "/evidence/",
            "/reports/deck.pptx",
            "/reports/annex-iv.zip",
            "/reports/export/pptx",
        }

    def _get_bucket_key(self, request: Request) -> str:
        """Get rate limit bucket key (API key or IP)."""
        # Prefer API key if available
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key}"
        
        # Fallback to IP
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    def _should_rate_limit(self, request: Request) -> bool:
        """Check if endpoint should be rate limited."""
        path = request.url.path
        return any(endpoint in path for endpoint in self.expensive_endpoints)

    def _consume_token(self, key: str) -> bool:
        """
        Try to consume a token from the bucket.
        
        Returns True if token available, False if rate limited.
        """
        tokens, last_refill = self.buckets[key]
        now = time.time()
        
        # Refill tokens based on elapsed time
        elapsed = now - last_refill
        tokens = min(self.rate_limit, tokens + (elapsed / self.window) * self.rate_limit)
        
        # Try to consume token
        if tokens >= 1:
            self.buckets[key] = (tokens - 1, now)
            return True
        else:
            self.buckets[key] = (tokens, now)
            return False

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Only rate limit expensive endpoints
        if self._should_rate_limit(request):
            key = self._get_bucket_key(request)
            
            if not self._consume_token(key):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Rate limit exceeded. Maximum {self.rate_limit} requests per minute.",
                        "retry_after": self.window,
                    },
                    headers={"Retry-After": str(self.window)},
                )

        return await call_next(request)

