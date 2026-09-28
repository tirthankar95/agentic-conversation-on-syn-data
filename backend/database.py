import re
import subprocess
from dataclasses import dataclass
from backend.observability import observation

@dataclass
class TableNames:
    id: str
    table_name: str

class SqlMachine:
    def __init__(self):
        self.create_table_names_table()

    def create_table_names_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.\"TableNames\" (
            id TEXT PRIMARY KEY,
            table_name TEXT NOT NULL UNIQUE,
            schema TEXT
        );
        """
        self.run(create_table_sql)
    
    @staticmethod
    def sql_literal(value):
        """Quote a value as a PostgreSQL string literal."""
        if value is None:
            return "NULL"
        return "'" + str(value).replace("'", "''") + "'"

    def insert_table_name(self, table_names, schema):
        for table_name in table_names:
            insert_sql = f"""
            INSERT INTO public."TableNames" (id, table_name, schema)
            VALUES (
                gen_random_uuid()::text,
                {self.sql_literal(table_name)},
                {self.sql_literal(schema)}
            )
            ON CONFLICT (table_name) DO NOTHING;
            """
            self.run(insert_sql)
    
    def select_table_names(self):
        select_sql = 'SELECT table_name FROM public."TableNames" ORDER BY table_name;'
        result = self.run(select_sql)
        if not result:
            return []
        # psql's default aligned output includes a header, separator, and row count.
        names = []
        for line in result.splitlines():
            value = line.strip()
            if not value or value in {'table_name'} or re.match(r'^\(\d+ rows?\)$', value.strip()):
                continue
            if set(value) <= {'-', '+', ' '}:
                continue
            if value.startswith('(') and value.endswith('rows)'):
                continue
            names.append(value)
        return names

    def run(self, sql_command):
        command = [
            "docker", "exec", "-i", "postgres-container",
            "psql", "-v", "ON_ERROR_STOP=1", "-X", "-U", "myuser", "-d", "mydb"
        ]
        with observation(
            name="postgres-query",
            as_type="tool",
            input={"sql": sql_command[:10000]},
            metadata={"sql_length": len(sql_command)},
        ) as query_observation:
            result = subprocess.run(
                command,
                input=sql_command,
                text=True,
                capture_output=True,
                check=False
            )
            if result.returncode != 0:
                print("Error executing SQL command:")
                print(sql_command)
                print("stderr:", result.stderr)
                error = Exception(
                    f"SQL command failed with return code {result.returncode}\nstderr: {result.stderr}"
                )
                if query_observation is not None:
                    query_observation.update(level="ERROR", status_message=str(error))
                raise error
            if query_observation is not None:
                query_observation.update(
                    output={
                        "stdout": result.stdout[:10000],
                        "stderr": result.stderr[:2000],
                        "return_code": result.returncode,
                    }
                )

        if result.stderr.strip():
            # psql can emit warnings on stderr even when command succeeds.
            print("psql warning:", result.stderr)

        if result.stdout.strip():
            print("Query executed successfully!")
            print("Output:\n", result.stdout)
        return result.stdout
