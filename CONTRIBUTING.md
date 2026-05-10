# Contributing to FINESE

Thank you for considering contributing to FINESE! We appreciate your interest in improving this data analysis platform. This document outlines the process for contributing to the project.

## How to Contribute

There are many ways to contribute to FINESE:

- Reporting bugs
- Suggesting new features
- Improving documentation
- Writing code
- Fixing bugs
- Adding new features

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/finese.git
   cd finese
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style Guidelines

- Follow PEP 8 guidelines for Python code
- Write clear, descriptive function and variable names
- Include docstrings for all public functions and classes
- Keep functions focused and small when possible
- Write meaningful commit messages

## Testing Your Changes

Before submitting a pull request, please:

1. Test your changes locally by running the application:
   ```bash
   streamlit run app.py
   ```
2. Verify that your changes work as expected
3. Ensure that you haven't broken any existing functionality
4. Add tests if applicable

## Submitting Changes

1. Commit your changes with a clear, descriptive message:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
2. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a pull request on the main repository
4. Fill out the pull request template with details about your changes

## Pull Request Process

1. Ensure your PR addresses a single issue or adds a single feature
2. Update documentation if needed
3. Add tests for new functionality if applicable
4. Make sure all tests pass
5. Wait for the maintainers to review your PR
6. Address any feedback from the reviewers

## Reporting Issues

When reporting issues, please include:

- A clear title and description
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, browser)
- Screenshots if applicable

## Feature Requests

When suggesting new features, please include:

- A clear description of the proposed feature
- Use cases for the feature
- Any potential challenges or considerations
- Mockups or examples if applicable

## Questions?

If you have questions about contributing, feel free to open an issue with the "question" label.

## Thank You!

Your contributions help make FINESE better for everyone. We appreciate your efforts to improve this tool for the data science community!