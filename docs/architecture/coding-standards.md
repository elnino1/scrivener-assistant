# Coding Standards

## 1. Environment & Setup
*   **Virtual Environment:**
    *   Development must be done inside a virtual environment named `.venv` located at the project root.
    *   Do NOT commit `.venv` to version control.
*   **Dependencies:**
    *   Manage dependencies in `pyproject.toml`.

## 2. Python Style Guide
*   **Imports:**
    *   All imports must be at the top of the file.
    *   Do NOT perform imports inside functions or methods (except for type checking guards if absolutely necessary to avoid circular deps).
*   **Module Structure:**
    *   Do NOT define classes in `__init__.py`.
    *   `__init__.py` should only be used to expose/export symbols from other modules to keep the API surface clean.
    *   Classes should reside in dedicated modules (e.g., `project.py`, `binder_parser.py`).

## 3. Type Annotations (MANDATORY)

### All Functions Must Have Complete Type Hints
*   **Parameters:** Every parameter MUST have a type annotation
*   **Return Types:** Every function MUST have a return type annotation
*   Use `None` for void functions
*   Use `Optional[T]` for nullable returns
*   Use proper collection types from `typing` module

**Examples:**
```python
# ✅ Good: Complete type annotations
def process_document(uuid: str, content: str) -> dict:
    return {"uuid": uuid, "length": len(content)}

def save_file(path: Path) -> None:
    path.write_text("data")

def find_item(id: str) -> Optional[Item]:
    return items.get(id)

# ❌ Bad: Missing type hints
def process_document(uuid, content):  # Missing parameter types!
    return {"uuid": uuid}

def save_file(path):  # Missing return type!
    pass
```

**Rationale:**
- Enables static type checking with `mypy`
- Improves IDE autocomplete and refactoring
- Self-documenting code
- Catches bugs at development time

## 4. Dependency Injection Pattern

### Prefer Constructor Injection Over Hardcoding
*   Inject dependencies via `__init__` rather than instantiating them inside classes
*   Makes code testable and flexible
*   Allows swapping implementations (e.g., file system vs. in-memory storage)

**Examples:**
```python
# ✅ Good: Dependencies injected
class MetadataManager:
    def __init__(self, scrivx_path: Path, backup_strategy: BackupStrategy):
        self.scrivx_path = scrivx_path
        self.backup = backup_strategy
    
    def save(self) -> None:
        self.backup.create(self.scrivx_path)
        # ... write logic

# ❌ Bad: Hardcoded dependency
class MetadataManager:
    def __init__(self, scrivx_path: Path):
        self.scrivx_path = scrivx_path
        self.backup = RollingBackup()  # Hardcoded! Cannot mock or swap
```

### Use Protocol/ABC for Abstractions
When possible, define interfaces using `Protocol` or `ABC`:

```python
from typing import Protocol

class Storage(Protocol):
    def save(self, key: str, value: str) -> None: ...
    def load(self, key: str) -> Optional[str]: ...

class PromptManager:
    def __init__(self, storage: Storage):
        self.storage = storage  # Can inject any Storage implementation
```

**Benefits:**
- Testability (inject mocks/fakes in tests)
- Flexibility (swap implementations without changing consuming code)
- Separation of concerns
- Easier to reason about dependencies
- Enables better testing isolation

## 5. Testing
*   Use `pytest`.
*   Tests should import public API from the package `__init__.py` when testing integration.
*   Use dependency injection fixtures for better test isolation.
