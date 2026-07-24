# syntax=docker/dockerfile:1

########################  Stage 1: build wheels  ########################
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
COPY requirements.txt .

# Build wheels for all dependencies so the final image needs no compilers.
RUN pip wheel --wheel-dir /wheels -r requirements.txt


########################  Stage 2: runtime  ############################
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Colombo

# Create a non-root user to run the bot.
RUN groupadd --system cyber && useradd --system --gid cyber --create-home cyber

WORKDIR /app

# Install dependencies from the pre-built wheels.
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy the application source.
COPY . .

# Logs directory owned by the non-root user.
RUN mkdir -p /app/logs && chown -R cyber:cyber /app

USER cyber

CMD ["python", "-u", "bot.py"]
