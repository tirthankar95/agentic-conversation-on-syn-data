"""List or delete tables in the project's PostgreSQL Docker container.

By default this connects to postgres-container and database mydb, matching
backend/database.py. It only targets tables in the public schema.
"""

import argparse
import subprocess
import sys


def psql(container: str, user: str, database: str, sql: str) -> str:
    command = [
        "docker", "exec", "-i", container,
        "psql", "-X", "-v", "ON_ERROR_STOP=1", "-U", user, "-d", database,
        "-A", "-t", "-c", sql,
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message)
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", default="postgres-container")
    parser.add_argument("--user", default="myuser")
    parser.add_argument("--database", default="mydb")
    parser.add_argument("--yes", action="store_true", help="skip interactive confirmation")
    args = parser.parse_args()

    try:
        tables = psql(
            args.container, args.user, args.database,
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;",
        ).splitlines()
        if not tables:
            print(f"No tables found in public schema of {args.database}.")
            return 0

        print(f"Tables in {args.database}.public:")
        for table in tables:
            print(f"  {table}")
        if not args.yes:
            confirmation = input(f'Type {args.database} to permanently drop these tables: ')
            if confirmation != args.database:
                print("Cancelled; no tables were dropped.")
                return 1

        # Identifiers are quoted safely by PostgreSQL's format(%I).
        drop_sql = """DO $do$
DECLARE item record;
BEGIN
  FOR item IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    EXECUTE format('DROP TABLE IF EXISTS public.%I CASCADE', item.tablename);
  END LOOP;
END $do$;"""
        psql(args.container, args.user, args.database, drop_sql)
        print(f"Dropped {len(tables)} table(s) from {args.database}.public.")
        return 0
    except (OSError, RuntimeError) as error:
        print(f"Could not access PostgreSQL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
