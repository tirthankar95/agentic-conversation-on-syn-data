from backend.database import SqlMachine
from backend.langchain_generate import GenWorkflow
from backend.prompts import (
    query_conversion, 
    table_entry,
    clean_query,
    beautify_response,
    sql_conversion
)

sql_machine = SqlMachine()
'''Main chatbot agent'''
main_chat_agent = GenWorkflow((sql_conversion, None), (clean_query, sql_machine.run), (beautify_response, None), name="main-chat-agent")
'''USED TO partially chat with the data in the data generation page'''
chat_agent = GenWorkflow((sql_conversion, None), (clean_query, None), name="data-generation-chat-agent")
'''USED TO GENERATE DUMMY DATA for TABLES'''
table_entry_agent = GenWorkflow((table_entry, None), (clean_query, None), name="table-entry-agent")
'''USED TO CONVERT SQL DDL TO Postgres COMPATIBLE DDL'''
query_conversion_agent = GenWorkflow((query_conversion, None), (clean_query, None), name="query-conversion-agent")


def parse_sql(file_content):
    prefixes = ["CREATE TABLE"]
    sql_commands, table_names = [], []
    parse_start, sql_command = False, ''
    for line in file_content.splitlines():
        for prefix in prefixes:
            if line.strip().startswith(prefix):
                parse_start = True 
                table_names.append(line.split()[2].strip('"'))
            if parse_start:
                sql_command += line + '\n'
                if line.strip().endswith(';'):
                    sql_commands.append(sql_command)
                    sql_command = ''
                    parse_start = False
    return table_names, sql_commands


def llm_generate(prompt, file_name, file_content, temperature, max_tokens):
    print(
        f"Prompt: {prompt}\n"
        f"File Name: {file_name}\n"
        f"Temperature: {temperature}\n"
        f"Max Tokens: {max_tokens}\n"
    )
    try:
        table_names, sql_commands = parse_sql(file_content)
        new_sql_commands = query_conversion_agent.workflow_response('\n'.join(sql_commands))
        print(f"Executing SQL Command:\n{new_sql_commands}")
        sql_machine.run(new_sql_commands)
        user_prompt = f'[INSTRUCTIONS]\n{prompt}\n\n[SQL SCHEMA]\n{new_sql_commands}'
        sql_machine.run(table_entry_agent.workflow_response(user_prompt))
        sql_machine.insert_table_name(table_names, new_sql_commands)
        return True
    except Exception as e:
        print(f"Error during generation: {e}")
        return False


def llm_chat_with_data_history(user_prompt: str, table_name: str, history: list):
    """Generate and run a request about a registered table, returning its result."""
    try:
        schema = sql_machine.run(
            f'SELECT schema FROM public."TableNames" WHERE table_name = {sql_machine.sql_literal(table_name)};'
        )
        table_data = sql_machine.run(f'SELECT * FROM {table_name} LIMIT 2;')
        conversation = "\n".join(
            f"{message['role']}: {message['content']}" for message in history
        )
        full_prompt = (
            f"[CONVERSATION HISTORY]\n{conversation or '(none)'}\n\n"
            f"[CURRENT REQUEST]\n{user_prompt}\n\n[TABLE NAME]\n{table_name}\n"
            f"[TABLE SCHEMA]\n{schema}\n[TABLE DATA]\n{table_data}"
        )
        result = main_chat_agent.workflow_response(full_prompt)
        return result.strip() or "Request completed successfully; the query returned no rows."
    except Exception as e:
        print(f"Error during chat with data: {e}")
        return f"Request failed: {e}"


def llm_chat_with_data(user_prompt: str, table_name: str):
    """Function to handle chat with data."""
    try:
        if table_name not in sql_machine.select_table_names():
            return f"Table '{table_name}' does not exist."
        user_prompt = f'[INSTRUCTIONS]\n{user_prompt}\n\n[TABLE NAME]\n{table_name}' + \
                    f'[TABLE SCHEMA]\n{sql_machine.run(f"SELECT schema FROM public.\"TableNames\" WHERE table_name = \'{table_name}\';")}' + \
                    f'[TABLE DATA]\n{sql_machine.run(f"SELECT * FROM {table_name} LIMIT 2;")}'
        sql_command = chat_agent.workflow_response(user_prompt)
        print(f"Executing SQL Command:\n{sql_command}")
        sql_machine.run(sql_command)
        return True
    except Exception as e:
        print(f"Error during chat with data: {e}")
        return False


if __name__ == "__main__":
    prompt = 'Create tables defined in the ddl schema file.'
    with open('examples/company_employee_schema.ddl', 'r') as f:
        file_content = f.read()
    llm_generate(prompt, 'company_employee_schema.ddl', file_content, temperature=0.7, max_tokens=512)
