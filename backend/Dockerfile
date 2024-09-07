# Use Python 3.10 base image
FROM python:3.10

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="$HOME/.local/bin:$PATH" && \
    poetry config virtualenvs.create false  # Install dependencies globally in the container environment

# Copy only the necessary files for dependency installation
COPY ./foodgram/pyproject.toml ./foodgram/poetry.lock* /app/

# Set the working directory
WORKDIR /app

# Install dependencies using Poetry
RUN /root/.local/bin/poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
