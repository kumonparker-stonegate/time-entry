import streamlit as st


def render():
    st.markdown(
        """
        <div style="text-align:center; padding: 1.5rem 0 0.5rem;">
            <div style="
                display:inline-block;
                background:#6DCFF6;
                color:#1A3A6B;
                font-size:1rem;
                font-weight:800;
                letter-spacing:0.18em;
                padding:0.35rem 1rem;
                border-radius:6px;
                margin-bottom:0.75rem;
            ">KUMON</div>
            <h1 style="color:#1A3A6B; font-size:1.9rem; font-weight:700; margin:0 0 0.3rem;">
                Time Entry System
            </h1>
            <p style="color:#667; font-size:0.95rem; margin:0 0 1.8rem;">
                Staff time tracking for Kumon of Parker Stonegate
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown(
            "<p style='text-align:center;color:#555;font-size:0.9rem;margin:0 0 0.6rem;'>"
            "Select your role to continue</p>",
            unsafe_allow_html=True,
        )
        if st.button("Employee", use_container_width=True, type="primary"):
            st.session_state.page = "employee_login"
            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Admin", use_container_width=True, type="secondary"):
            st.session_state.page = "admin_login"
            st.rerun()
