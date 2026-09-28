from backend.database import SqlMachine
from backend.langchain_backend import llm_chat_with_data_history

sql_machine = SqlMachine()
MAX_HISTORY = 10

def apply_chat(st):
    st.header("Talk to your data")
    st.caption("Ask questions about a table or request changes to its data.")
    available_tables = sql_machine.select_table_names()
    if not available_tables:
        st.info("No tables are registered yet. Generate data first.")
        return
    selected_table = st.selectbox(
        "Choose a table",
        options=available_tables,
        key="talk_to_data_table",
        label_visibility="collapsed",
    )
    history_key = f"talk_to_data_history:{selected_table}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []
    history = st.session_state[history_key]
    if not history:
        with st.chat_message("assistant"):
            st.write(f"Hello! Ask me about **{selected_table}** or request a change to its data.")
    else:
        for message in history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    if prompt := st.chat_input(f"Ask about {selected_table}..."):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Working with the selected table..."):
                response = llm_chat_with_data_history(
                    user_prompt=prompt,
                    table_name=selected_table,
                    history=history,
                )
            st.markdown(response)
        history.append({"role": "assistant", "content": response})
        # Drop older messages to keep the history manageable [SIMPLE]
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        st.session_state[history_key] = history
