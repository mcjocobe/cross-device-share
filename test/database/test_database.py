import pytest
import docker

from pathlib import Path

import time

DATABASE_CONTAINER_NAME = "device-sharing"
DATABASE_CONTAINER_PORT = 5432
DATABASE_NAME = "device-sharing"
DATABASE_PASSWORD = "secretpassword"
DATABASE_USER = "superuser"
MIGRATIONS_FOLDER = Path(__file__).parents[1] / "migrations"


@pytest.fixture
def docker_client():
    return docker.from_env()
 

@pytest.fixture
def empty_database(docker_client):
    if docker_client.containers.list(filters={"name": DATABASE_CONTAINER_NAME}):
        docker_client.containers.get(DATABASE_CONTAINER_NAME).remove(force=True)
    container = docker_client.containers.run(
        "postgres",
        auto_remove=True,
        environment={
            "POSTGRES_DB": DATABASE_NAME,
            "POSTGRES_PASSWORD": DATABASE_PASSWORD,
            "POSTGRES_USER": DATABASE_USER,
        },
        detach=True,
        name=DATABASE_CONTAINER_NAME,
        ports={DATABASE_CONTAINER_PORT: DATABASE_CONTAINER_PORT},
    )
    while "running" != container.status:
        time.sleep(1)
        container.reload()
    yield
    container.stop()

@pytest.fixture
def database_url():
    return f"db:postgres://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:{DATABASE_CONTAINER_PORT}/{DATABASE_NAME}"

def test_apply_migrations(empty_database):
    empty_database
