<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# OCR Agent Project Instructions

This is a Python project for OCR (Optical Character Recognition) functionality. When working on this project, please follow these guidelines:

## Code Style and Standards
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use docstrings for all classes and functions
- Maintain consistent logging throughout the application
- Use black for code formatting (line length: 88 characters)

## Project Structure
- `src/`: Main source code directory
- `tests/`: Unit tests using pytest
- `requirements.txt`: Production dependencies
- `requirements-dev.txt`: Development dependencies

## Testing
- Write unit tests for all new functionality
- Use pytest as the testing framework
- Aim for high test coverage
- Mock external dependencies in tests

## Dependencies
- Use numpy and pandas for data processing
- Use requests for HTTP operations
- Include proper error handling and logging
- Use python-dotenv for environment configuration

## Development Workflow
- Use virtual environments for dependency isolation
- Run tests before committing changes
- Use pre-commit hooks for code quality
- Follow semantic versioning for releases
