def apply_custom_styles(st):
    st.markdown(
        """
        <style>
        /* Force Primary Buttons to be solid Black with White Text */
        button[kind="primary"] {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
        }
        button[kind="primary"]:hover {
            background-color: #222222 !important;
            color: #ffffff !important;
            border-color: #222222 !important;
        }
        button[kind="primary"] * {
            color: #ffffff !important;
        }

        /* Force Secondary Buttons to be Light Gray with Black Text */
        button[kind="secondary"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc !important;
        }
        button[kind="secondary"]:hover {
            background-color: #f0f0f0 !important;
            color: #000000 !important;
            border-color: #000000 !important;
        }
        button[kind="secondary"] * {
            color: #000000 !important;
        }

        /* Change slider color to black */
        div[data-baseweb="slider"] div {
            background-color: #000000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )