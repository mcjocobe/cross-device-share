from pathlib import Path

import docker
import psycopg2
import pytest
import sqlalchemy
import subprocess
import time
import os

import alembic
from alembic.config import Config
from alembic import command, autogenerate
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

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
def database_port(docker_client):
    container_port = DATABASE_CONTAINER_PORT
    for container in docker_client.containers.list():
        if str(container_port) in str(container.attrs["NetworkSettings"]["Ports"]):
            container_port += 10
    return container_port


@pytest.fixture
def empty_database(database_port, docker_client):
    DATABASE_CONTAINER_PORT = database_port
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
def database_url(empty_database):
    return f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@localhost:{DATABASE_CONTAINER_PORT}/{DATABASE_NAME}"


@pytest.fixture
def database_connection(database_url):
    sqlalchemy.url = database_url
    engine = sqlalchemy.create_engine(database_url)
    return engine.connect()


@pytest.fixture
def set_up_alembic(database_url, database_connection):
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    alembic_script = ScriptDirectory.from_config(alembic_cfg)
    alembic_env = EnvironmentContext(alembic_cfg, alembic_script)
    alembic_env.configure(connection=database_connection)
    alembic_context = alembic_env.get_context()

    command.upgrade(alembic_cfg, "head")


@pytest.fixture
def database(empty_database, set_up_alembic):
    set_up_alembic


@pytest.mark.usefixtures("database")
def test_apply_migrations(database_connection):
    conn = database_connection
    with database_connection as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT TABLE_NAME FROM information_schema.tables;")
        )
        schemas = [row[0] for row in result]

    assert "users" in schemas


def test_downgrade_migration():
    # subprocess.Popen("alembic downgrade base", shell=True)
    pass
