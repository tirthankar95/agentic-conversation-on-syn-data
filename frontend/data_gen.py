from backend.langchain_backend import (
    llm_generate,
    llm_chat_with_data
)
from backend.database import SqlMachine

sql_machine = SqlMachine()

def apply_row1(st):
    # Row 1: Top Element
    top_row = st.container(border=True)
    with top_row:
        prompt = st.text_input(
            "Prompt",
            placeholder="Enter your prompt here...",
            help="Enter additional instructions which would go with the DDL schema to generate synthetic data."
        )
        uploaded_file = st.file_uploader(
            "Upload DDL Schema",
            type=["ddl", "sql"],
            key="ddl_upload",
        )
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        with col2:
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=1,
                value=65536,
                key="gen_max_tokens"
            )
        if st.button(
            "Generate",
            type="primary",
            icon=":material/auto_awesome:",
        ):
            if not prompt.strip():
                st.warning("Please enter a prompt.")
                return
            if uploaded_file is None:
                st.warning("Please upload a DDL schema file.")
                return
            file_content = uploaded_file.read().decode("utf-8", errors="ignore")
            if llm_generate(
                prompt=prompt,
                file_name=uploaded_file.name,
                file_content=file_content,
                temperature=temperature,
                max_tokens=int(max_tokens),
            ):
                st.toast("Dummy generate called successfully.", icon="✅")
            else:
                st.toast("Dummy generate failed. Please check the logs for more details.", icon="❌")


def apply_row2(st):
    # Row 2: Bottom Element
    bottom_row = st.container(border=True)
    with bottom_row:
        header, select_col = st.columns(2)
        
        available_files = [
            "Select a file..."
        ]
        sql_machine_result = sql_machine.select_table_names()
        available_files.extend(sql_machine_result)
        with header:
            st.write("#### Data Preview")
        with select_col:
            selected_file = st.selectbox(
                "",
                options=available_files,
                index=0,
                help="Choose a schema to inspect its generated contents.",
            )
        st.divider()
        if selected_file and selected_file != "Select a file...":
            st.info(f"Displaying content preview for **{selected_file}**...")
            result = sql_machine.run(f"SELECT * FROM {selected_file};")
            st.code(
                f"""{result}""",
                language="sql",
            )
            user_prompt = st.chat_input("Query to modify the table entries...")
            if user_prompt:
                if llm_chat_with_data(
                    user_prompt=user_prompt,
                    table_name=selected_file,
                    history=[]
                ):
                    st.toast("Modification successful.", icon="✅")
                else:
                    st.toast("Try again with more detailed prompt.", icon="❌")
        else:
            st.text("No file selected.")



def apply_data_gen(st):
    apply_row1(st)
    apply_row2(st)

