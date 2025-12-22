# Running Integration Tests

This project uses **pytest** for integration testing against a temporary MikroTik RouterOS container.

1. Make sure you have **Docker** installed and running.
2. Install test dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```
3. Run the tests:

   ```bash
   pytest -v
   ```

   This will:

   * Spin up a MikroTik RouterOS container
   * Run integration tests (create, list, and delete user)
   * Tear down the container automatically

By default, tests are marked with `@pytest.mark.integration`.
You can run only integration tests with:

```bash
pytest -m integration -v
```
