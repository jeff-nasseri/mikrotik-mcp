def pytest_ignore_collect(collection_path, config):
    name = getattr(collection_path, "name", str(collection_path))
    if isinstance(name, str) and name.startswith("pytest-cache-files-"):
        return True
    if name == ".pytest_cache":
        return True
    return False
