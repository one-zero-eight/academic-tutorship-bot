import importlib
import inspect
from pathlib import Path

from src.support_daemon.server.queries.base import Query


def collect_queries() -> list[type[Query]]:
    """Collects all Query subclasses from sibling modules"""
    queries = []
    current_path = Path(__file__).parent

    # Iterate through all Python files in the same directory
    for file_path in current_path.glob("*.py"):
        # Skip __init__.py itself
        if file_path.name == "__init__.py":
            continue

        # Get the module name (filename without .py extension)
        module_name = file_path.stem

        # Construct the full module path
        full_module_path = f"src.support_daemon.server.queries.{module_name}"

        try:
            # Import the module
            module = importlib.import_module(full_module_path)

            # Find all Query subclasses in the module
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Query)
                    and obj != Query  # Exclude the base class itself
                    and obj.__module__ == full_module_path
                ):  # Make sure it's from this module
                    queries.append(obj)

        except ImportError as e:
            print(f"Warning: Could not import module {full_module_path}: {e}")
        except Exception as e:
            print(f"Warning: Error processing module {full_module_path}: {e}")

    return queries


QUERIES = collect_queries()


def determine_query(query: str) -> type[Query]:
    args = query.split()
    for QueryType in QUERIES:
        if args[0] == QueryType.name:
            return QueryType
    raise ValueError(f'unknown query "{args[0]}"')
