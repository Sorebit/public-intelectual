import pathlib

schema = ""
schema_path = pathlib.Path(__file__).parent / "schema.sql"

with open(schema_path, 'r') as file:
    schema = file.read()
