"""Custom exceptions for Threads.net scraping operations."""


class ThreadsScraperException(Exception):
    """Base exception for the Threads scraper."""


class NetworkError(ThreadsScraperException):
    """Raised when network-level issues occur."""


class ScrapingError(ThreadsScraperException):
    """Raised when scraping fails (page structure changed, unexpected payload)."""


class PageNotFoundError(ThreadsScraperException):
    """Raised when a Threads profile returns 404 or does not exist."""
