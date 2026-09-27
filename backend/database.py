import subprocess
from dataclasses import dataclass

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
    
    def insert_table_name(self, table_name, schema):
        insert_sql = f"""
        INSERT INTO public.\"TableNames\" (id, table_name, schema)
        VALUES (gen_random_uuid()::text, '{table_name}', '{schema}')
        ON CONFLICT (table_name) DO NOTHING;
        """
        self.run(insert_sql)
    
    def select_table_names(self):
        select_sql = "SELECT id, table_name FROM public.\"TableNames\";"
        result = self.run(select_sql)
        if not result:
            return []
        parsed_result = []
        for line in result.splitlines():
            line = line.strip()
            row = line.split('|')
            if len(row) == 2 and row[0].strip() != 'id' and row[1].strip() != 'table_name':
                parsed_result.append(row[1].strip())
        return parsed_result

    def run(self, sql_command):
        command = [
            "docker", "exec", "-i", "postgres-container",
            "psql", "-v", "ON_ERROR_STOP=1", "-X", "-U", "myuser", "-d", "mydb"
        ]
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
            raise Exception(f"SQL command failed with return code {result.returncode}\nstderr: {result.stderr}")

        if result.stderr.strip():
            # psql can emit warnings on stderr even when command succeeds.
            print("psql warning:", result.stderr)

        if result.stdout.strip():
            print("Query executed successfully!")
            print("Output:\n", result.stdout)
        return result.stdout