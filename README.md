# Cache Tools
This library provides a decorator for caching functions

```python
from cache_tools import cache


# Add cache so you don't always have to access the database, for example
@cache(namespace='todo')
async def get_todos(title=None, status=None):
    """Get all todos filtering by title or status."""


# Clear all caches in all namespaces so that no function has the result lagged to the database for example
@cache.clear(namespaces=['todo'])
async def add_todo(title, status=False):
    """Add todo."""
```
