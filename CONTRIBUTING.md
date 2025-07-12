# Contributing to SUMO Helper

Thank you for your interest in contributing to SUMO Helper! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue template** and provide all requested information
3. **Include steps to reproduce** the problem
4. **Add relevant logs** and error messages
5. **Specify your environment** (OS, Python version, Node.js version)

### Feature Requests

When requesting features:

1. **Describe the use case** clearly
2. **Explain the expected behavior**
3. **Consider the impact** on existing functionality
4. **Provide examples** if possible

### Code Contributions

#### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker (optional, for testing)

#### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/sumo-helper.git
   cd sumo-helper
   ```

2. **Set up the backend**
   ```bash
        cd backend
     python3 -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     pip install -r requirements-dev.txt  # For development dependencies
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Create a development branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Workflow

1. **Start development servers**
   ```bash
   # Backend (in one terminal)
   cd backend
   source venv/bin/activate
   python main.py

   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Write tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   npm run lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python (Backend)

- **Follow PEP 8** style guidelines
- **Use type hints** for function parameters and return values
- **Write docstrings** for all functions and classes
- **Use meaningful variable names**
- **Keep functions small and focused**

Example:
```python
from typing import Dict, List, Optional

def process_network_data(network_id: str, config: Dict[str, any]) -> Optional[List[str]]:
    """
    Process network data and return processed results.
    
    Args:
        network_id: The unique identifier for the network
        config: Configuration dictionary for processing
        
    Returns:
        List of processed results or None if processing fails
        
    Raises:
        ValueError: If network_id is invalid
    """
    if not network_id:
        raise ValueError("Network ID cannot be empty")
    
    # Implementation here
    return results
```

### JavaScript/React (Frontend)

- **Use functional components** with hooks
- **Follow ESLint rules** and fix all warnings
- **Use meaningful component and variable names**
- **Keep components small and focused**
- **Use TypeScript** for new components when possible

Example:
```jsx
import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

/**
 * Network visualization component
 * 
 * @param {Object} props - Component props
 * @param {string} props.networkId - Network identifier
 * @param {Function} props.onNodeClick - Callback for node clicks
 * @returns {JSX.Element} Network visualization
 */
const NetworkVisualization = ({ networkId, onNodeClick }) => {
  const [nodes, setNodes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load network data
    loadNetworkData(networkId)
  }, [networkId])

  return (
    <div className="network-visualization">
      {loading ? (
        <div>Loading...</div>
      ) : (
        <NetworkGraph nodes={nodes} onNodeClick={onNodeClick} />
      )}
    </div>
  )
}

NetworkVisualization.propTypes = {
  networkId: PropTypes.string.isRequired,
  onNodeClick: PropTypes.func.isRequired
}

export default NetworkVisualization
```

### Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

Examples:
```
feat: add network export functionality
fix: resolve memory leak in simulation service
docs: update API documentation
style: format code according to PEP 8
refactor: extract network processing logic
test: add unit tests for map service
chore: update dependencies
```

## 🧪 Testing

### Backend Testing

- **Write unit tests** for all new functionality
- **Use pytest** as the testing framework
- **Aim for 80%+ code coverage**
- **Test both success and error cases**

Example test:
```python
import pytest
from services.map_service import MapService

class TestMapService:
    def setup_method(self):
        self.map_service = MapService()
    
    def test_select_area_valid_coordinates(self):
        """Test selecting area with valid coordinates"""
        result = self.map_service.select_area(
            north=40.5, south=40.4, east=-3.7, west=-3.8
        )
        assert result is not None
        assert 'map_id' in result
    
    def test_select_area_invalid_coordinates(self):
        """Test selecting area with invalid coordinates"""
        with pytest.raises(ValueError):
            self.map_service.select_area(
                north=40.5, south=40.6, east=-3.7, west=-3.8
            )
```

### Frontend Testing

- **Write component tests** using React Testing Library
- **Test user interactions** and component behavior
- **Mock API calls** appropriately
- **Test error states** and loading states

Example test:
```jsx
import { render, screen, fireEvent } from '@testing-library/react'
import MapSelection from '../pages/MapSelection'

describe('MapSelection', () => {
  test('renders map selection interface', () => {
    render(<MapSelection />)
    expect(screen.getByText('Select Map Area')).toBeInTheDocument()
  })

  test('handles area selection', async () => {
    render(<MapSelection />)
    const selectButton = screen.getByText('Select Area')
    fireEvent.click(selectButton)
    // Add assertions for expected behavior
  })
})
```

## 📚 Documentation

### Code Documentation

- **Document all public APIs** with clear docstrings
- **Include examples** in docstrings
- **Update README.md** for new features
- **Add inline comments** for complex logic

### API Documentation

- **Update OpenAPI schemas** for new endpoints
- **Provide example requests/responses**
- **Document error codes** and messages

## 🔍 Code Review Process

1. **Create a pull request** with a clear description
2. **Link related issues** in the PR description
3. **Ensure all tests pass** before requesting review
4. **Address review comments** promptly
5. **Squash commits** before merging

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
```

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Docker images built and tested
- [ ] Release notes prepared

## 🆘 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and API docs first

## 📄 License

By contributing to SUMO Helper, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SUMO Helper! 🎉 