import streamlit as st


def render():
    st.markdown(
        """
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <div style="
                display:inline-block;
                background:#003087;
                color:white;
                font-size:1.1rem;
                font-weight:800;
                letter-spacing:0.18em;
                padding:0.4rem 1.1rem;
                border-radius:6px;
                margin-bottom:1rem;
            ">KUMON</div>
            <h1 style="color:#003087; font-size:2rem; font-weight:700; margin:0.3rem 0 0.2rem;">
                Time Entry System
            </h1>
            <p style="color:#667; font-size:1rem; margin:0;">
                Staff time tracking for Kumon of Parker Stonegate
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            """
            <div style="
                background:white;
                border:1px solid #C8D4EF;
                border-radius:12px;
                padding:2rem 2rem 1.5rem;
                box-shadow:0 2px 12px rgba(0,48,135,0.08);
            ">
            <p style="text-align:center;color:#445;font-size:0.95rem;margin-top:0;margin-bottom:1.5rem;">
                Select your role to continue
            </p>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Employee", use_container_width=True, type="primary"):
            st.session_state.page = "employee_login"
            st.rerun()

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        if st.button("Admin", use_container_width=True, type="secondary"):
            st.session_state.page = "admin_login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
