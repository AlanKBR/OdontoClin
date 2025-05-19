# OdontoClin

A dental clinic management system built with Flask. This application helps manage patient records, treatments, appointments, and financial information for dental clinics.

## Features

- Patient management
- Treatment planning and tracking
- User authentication and role-based access
- Financial tracking for treatments

## Development Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd prototipo
```

2. Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Code Quality Tools

This project uses several tools to ensure code quality:

- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Style guide enforcer
- **pylint**: Code analysis

#### VS Code Integration

If you're using VS Code, the workspace settings are already configured to:
- Format code on save using Black
- Sort imports using isort
- Show linting errors from flake8 and pylint

#### Manual Linting

You can run the linting tools manually using:

```bash
# On Linux/macOS
python lint.py

# On Windows
python lint.py
```

### Git Pre-commit Hook

A pre-commit hook is set up to run the linting checks before each commit. If the linting fails, the commit will be blocked.

### Linting Configuration

- **Black**: 100 character line length
- **isort**: Black profile compatibility
- **flake8**: 100 character line length, ignoring specific errors
- **pylint**: Customized rules in .pylintrc file
