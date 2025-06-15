"""
Main application file for OdontoClin.
"""

import datetime
import secrets
from datetime import timezone
from typing import Callable

# Import the application factory function
from app import create_app  # pylint: disable=import-self

# Create the application instance
app = create_app()


@app.context_processor
def inject_now() -> dict[str, datetime.datetime]:
    """
    Injects the current UTC datetime into Jinja2 templates.

    This allows templates to access the current time via the `now` variable.
    The datetime object is timezone-aware and set to UTC.

    Returns:
        A dictionary where the key 'now' maps to the current UTC datetime.
    """
    return {"now": datetime.datetime.now(timezone.utc)}


@app.context_processor
def inject_csp_nonce() -> dict[str, Callable[[], str]]:
    """
    Provides a Content Security Policy (CSP) nonce for Jinja2 templates.
    Provides a Content Security Policy (CSP) nonce for Jinja2 templates.

    This function generates a unique nonce (number used once) that can be
    used in CSP headers and inline scripts or styles to allow their execution
    while mitigating cross-site scripting (XSS) risks.

    The nonce is provided as a callable (lambda function) within the dictionary
    to ensure that a fresh nonce is generated for each request if needed, although
    in this specific implementation, the nonce is generated once per application
    context setup for this processor.

    Returns:
        A dictionary where the key 'csp_nonce' maps to a lambda function
        that returns the generated CSP nonce string.
    """
    nonce = secrets.token_hex(16)
    return {"csp_nonce": lambda: nonce}


if __name__ == "__main__":
    app.run(debug=True)
