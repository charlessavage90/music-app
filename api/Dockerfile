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

# Run as an unprivileged user (G3-S6). Everything above ran as root and stays
# root-owned and world-readable, which is all the service needs: it writes
# nothing to disk. The graph is fetched from S3 straight into memory
# (artifact_source.default_reader), the clip cache is DynamoDB or in-process,
# logs go to stdout, and UV_COMPILE_BYTECODE above means no __pycache__ is
# written at import. The UID is numeric so a runtime can verify non-root
# without resolving a name. No home directory: boto3 reads ~/.aws only if it
# exists, and App Runner supplies credentials through the instance role.
RUN groupadd --gid 10001 artistpath \
    && useradd --uid 10001 --gid 10001 --no-create-home \
        --home-dir /nonexistent --shell /usr/sbin/nologin artistpath
USER 10001:10001

EXPOSE 8000
CMD ["uvicorn", "artistpath_api.app:build_default_app", "--factory", \
     "--host", "0.0.0.0", "--port", "8000"]
