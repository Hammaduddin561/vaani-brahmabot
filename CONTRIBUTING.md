# Contributing to VAANI - The BrahmaBot

Thank you for your interest in contributing to VAANI! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** following our guidelines
5. **Test your changes** thoroughly
6. **Submit a pull request**

## 📋 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Code editor (VS Code recommended)

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/vaani-brahmabot.git
cd vaani-brahmabot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Copy environment template
cp .env.example .env

# Run tests
python -m pytest tests/

# Start development server
python enhanced_app.py
```

## 🛠️ Development Guidelines

### Code Style
- **Python**: Follow PEP 8 style guide
- **Line Length**: Maximum 88 characters (Black formatter)
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type annotations for function parameters and returns

### Code Quality Tools
```bash
# Format code with Black
black .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .

# Sort imports with isort
isort .
```

### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `perf`: Performance improvements

Examples:
```
feat(api): add real-time satellite tracking endpoint
fix(whatsapp): resolve message processing timeout issue
docs(readme): update installation instructions
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_space_engine.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests
- Place tests in `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Include both positive and negative test cases
- Mock external dependencies

Example test structure:
```python
import pytest
from unittest.mock import patch, MagicMock
from your_module import YourClass

class TestYourClass:
    def test_successful_operation(self):
        # Test successful case
        pass
    
    def test_error_handling(self):
        # Test error cases
        pass
    
    @patch('your_module.external_dependency')
    def test_with_mocking(self, mock_external):
        # Test with mocked dependencies
        pass
```

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include parameter types and descriptions
- Provide usage examples for complex functions

Example docstring:
```python
def process_space_query(query: str, context: dict = None) -> dict:
    """Process a space-related query using AI.
    
    Args:
        query: The user's question about space
        context: Optional conversation context
        
    Returns:
        Dict containing response, confidence, and metadata
        
    Raises:
        ValueError: If query is empty or invalid
        
    Example:
        >>> response = process_space_query("Where is the ISS?")
        >>> print(response['answer'])
        "The ISS is currently over the Pacific Ocean..."
    """
```

### API Documentation
- Update OpenAPI schemas for new endpoints
- Provide request/response examples
- Document error codes and messages
- Include authentication requirements

## 🚨 Issue Reporting

### Bug Reports
Include:
- **Environment**: OS, Python version, VAANI version
- **Steps to reproduce**: Detailed reproduction steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

### Feature Requests
Include:
- **Problem**: What problem does this solve?
- **Solution**: Proposed solution or approach
- **Alternatives**: Other solutions considered
- **Context**: Additional context or examples

## 🔧 Code Contribution Areas

### High Priority
- **Performance Optimization**: Memory usage, response times
- **Test Coverage**: Increase test coverage to >90%
- **Documentation**: API docs, tutorials, examples
- **Accessibility**: UI/UX improvements
- **Mobile Responsiveness**: Better mobile experience

### Feature Ideas
- **Multi-language Support**: Hindi, other Indian languages
- **Voice Interface**: Speech-to-text integration
- **Advanced Analytics**: Usage metrics, performance insights
- **Plugin System**: Extensible architecture
- **Real-time Collaboration**: Multi-user features

### Technical Debt
- **Code Refactoring**: Improve code organization
- **Dependency Updates**: Keep dependencies current
- **Security Improvements**: Authentication, authorization
- **Performance Monitoring**: Better observability
- **Error Handling**: Robust error recovery

## 📝 Pull Request Process

### Before Submitting
1. **Update documentation** if needed
2. **Add/update tests** for new functionality
3. **Run full test suite** and ensure all tests pass
4. **Check code quality** with linting tools
5. **Update CHANGELOG.md** with your changes

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Changelog updated
```

### Review Process
1. **Automated checks** must pass
2. **Maintainer review** required
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Merge** when approved

## 🏆 Recognition

Contributors will be:
- **Listed** in CONTRIBUTORS.md
- **Mentioned** in release notes
- **Credited** in documentation
- **Featured** in project updates

## 📞 Communication

### Getting Help
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews

### Community Guidelines
- **Be respectful** and inclusive
- **Help others** learn and contribute
- **Follow** the code of conduct
- **Share knowledge** and experiences

## 🚀 Next Steps

1. **Explore the codebase** to understand the architecture
2. **Check issues** labeled "good first issue" or "help wanted"
3. **Join discussions** to understand project direction
4. **Start small** with documentation or bug fixes
5. **Ask questions** if you need clarification

Thank you for contributing to VAANI! Together, we're building the future of AI-powered space knowledge assistance. 🌌✨