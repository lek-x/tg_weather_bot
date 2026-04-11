# Deployment Checklist

Use this file when the task involves CI/CD, Docker, release automation, Terraform, or environment rollout issues.

## CI/CD

- Match local reproduction commands to the failing workflow step.
- Check workflow triggers, branch filters, matrix values, working directory, and artifact paths.
- Verify the dependency install command matches the repository's package manager.
- Confirm secrets and env vars are referenced consistently and only where needed.

## Docker

- Verify build context and `COPY` paths.
- Confirm the image includes runtime dependencies, templates, and static assets.
- Check the exposed port, entrypoint, command, and healthcheck behavior.
- Ensure the container runs as expected with the repo's documented environment variables.

## Terraform Or Infra

- Check variable names, defaults, and environment-specific overrides.
- Review module inputs and outputs before editing resources.
- Prefer validation or plan-style checks when the repo exposes them.
- Call out remote-state, provider, or credential limitations explicitly.

## Release Safety

- Avoid mixing unrelated cleanup into deployment fixes.
- Prefer reversible changes and clear logging over clever automation.
- Document any manual step that still has to happen after the code change.
