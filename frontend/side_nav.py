def apply_side_bar(st):
    with st.sidebar:
        st.title("Chat Data Faker")
        
        # Clicking the text name acts as a button
        if "active_page" not in st.session_state:
            st.session_state.active_page = "Data Generation"
            
        if st.button("Data Generation", use_container_width=True, key="nav_data_gen"):
            st.session_state.active_page = "Data Generation"

        if st.button("Talk to your data", use_container_width=True, key="nav_talk_data"):
            st.session_state.active_page = "Talk to your data"
        
        st.divider()
        
        # Sidebar controls specific to active page mode
        if st.session_state.active_page != "Data Generation":
            st.write("### Chat Settings")
            st.selectbox("Model", ["GPT-4o", "Claude 3.5 Sonnet", "Llama 3"])
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
