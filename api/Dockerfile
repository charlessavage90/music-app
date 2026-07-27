# The release artifact. With no CI (DEP-3, DEP-15) this image is what ships,
# so it installs the committed lockfile exactly rather than re-resolving
# (DEP-32). `uv sync --frozen` fails loudly if uv.lock and pyproject.toml
# disagree, which is the property being bought.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# pyproject + lock first so the dependency layer caches across source edits.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "artistpath_api.app:build_default_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000"]
