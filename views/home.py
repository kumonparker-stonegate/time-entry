import streamlit as st


def render():
    st.markdown(
        """
        <style>
        .home-title { font-size: 2.4rem; font-weight: 700; color: #003087; text-align: center; margin-bottom: 0.2rem; }
        .home-sub   { text-align: center; color: #666; margin-bottom: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="home-title">Kumon Time Entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-sub">Staff time tracking system</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        if st.button("Employee Login", use_container_width=True, type="primary"):
            st.session_state.page = "employee_login"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Admin Login", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()
