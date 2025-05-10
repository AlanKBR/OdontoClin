"""
Main application file for OdontoClin.
"""

import datetime
import secrets
from datetime import timezone

# Import the application factory function
from app import create_app  # pylint: disable=import-self

# Create the application instance
app = create_app()


@app.context_processor
def inject_now():
    """Inject current UTC time into templates."""
    return {"now": datetime.datetime.now(timezone.utc)}


@app.context_processor
def inject_csp_nonce():
    """Provide a CSP nonce for templates."""
    nonce = secrets.token_hex(16)
    return {"csp_nonce": lambda: nonce}


if __name__ == "__main__":
    app.run(debug=True)
