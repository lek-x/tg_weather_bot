# Python Service Checklist

Use this file when the task involves Python runtime behavior, dependency management, packaging, or service startup failures.

## Inspect

- Read `pyproject.toml`, `requirements.txt`, or lockfiles first.
- Identify the project toolchain: `uv`, `poetry`, `pip`, `pytest`, `ruff`, `mypy`, or framework-specific commands.
- Find the real entrypoint: `main.py`, `app.py`, `manage.py`, module execution, or container entrypoint.
- Trace required environment variables and external services before editing code.

## Common Failure Patterns

- Dependency installed locally but missing in container or CI
- Python version mismatch between local, CI, and runtime image
- Import path depends on working directory side effects
- Startup fails because env vars are missing or parsed too early
- Async job, scheduler, or webhook path is untested while HTTP path works
- Retry or exception handling hides the real failure mode in logs

## Preferred Fix Patterns

- Align one dependency source of truth instead of patching multiple files inconsistently.
- Move configuration reads to startup boundaries when import-time side effects break tests or commands.
- Add narrowly scoped logging around external calls or startup branches.
- Add regression tests close to the failing code path when a test harness already exists.
- Keep operational defaults explicit and safe.

## Verification Ideas

- Run the repo's existing install command.
- Run targeted tests for the changed module or endpoint.
- Start the service with representative env vars when possible.
- If containerized, verify the same command used by the container entrypoint.
