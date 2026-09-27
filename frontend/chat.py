def apply_chat(st):
    # --- TALK TO YOUR DATA VIEW ---
    st.header("Talk to Your Data")
    st.caption("Ask questions about your uploaded schemas and generated data.")
    
    chat_container = st.container(border=True)
    with chat_container:
        st.chat_message("assistant").write("Hello! Ask me anything about your generated synthetic dataset.")
        
    st.chat_input("Ask a query about your tables...")