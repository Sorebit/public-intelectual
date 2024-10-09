from contextlib import contextmanager
import logging
import pathlib
import sqlite3

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


schema = ""
schema_path = pathlib.Path(__file__).parent / "schema.sql"

with open(schema_path, 'r') as file:
    schema = file.read()


def dict_row_factory(cursor: sqlite3.Cursor, row):
    fields = [column[0] for column in cursor.description]
    return {k: v for k, v in zip(fields, row)}


@contextmanager
def connection(db_uri: str):
    logger.debug(f"Connecting to {db_uri}")
    connection = sqlite3.connect(db_uri, uri=True)
    connection.row_factory = dict_row_factory
    yield connection
    logger.debug(f"Closing connection to {db_uri}")
    connection.rollback()
    connection.close()
