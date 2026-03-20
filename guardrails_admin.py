# ============================================================
# guardrails_admin.py — Dynamic Guardrails Admin Panel
# Password protected UI to manage all compliance rules
# ============================================================

import streamlit as st
from guardrails_db import (
    get_exclusions, get_age_restrictions, get_prior_auth_triggers, get_fraud_signals,
    add_exclusion, delete_exclusion, toggle_exclusion,
    add_age_restriction, delete_age_restriction, toggle_age_restriction,
    add_prior_auth, delete_prior_auth, toggle_prior_auth,
    add_fraud_signal, delete_fraud_signal, toggle_fraud_signal,
)

ADMIN_PASSWORD = "nidanai@admin"
PLANS = ["Ayushman Bharat (PMJAY)", "BSKY (Odisha)", "ESIC", "CGHS", "Private PPO"]


def _check_auth():
    if 'admin_auth' not in st.session_state:
        st.session_state['admin_auth'] = False

    if not st.session_state['admin_auth']:
        st.markdown("""
            <div style="background:#111827; border:1px solid #1e293b; border-radius:12px;
                        padding:32px; max-width:400px; margin:40px auto; text-align:center;">
                <div style="font-size:32px; margin-bottom:8px;">🔐</div>
                <div style="font-size:18px; font-weight:700; color:#e2e8f0; margin-bottom:4px;">
                    Admin Access Required
                </div>
                <div style="font-size:13px; color:#64748b;">
                    Guardrails management ke liye password chahiye
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pwd = st.text_input("Admin Password", type="password", key="admin_pwd_input")
            if st.button("🔓 Login", use_container_width=True):
                if pwd == ADMIN_PASSWORD:
                    st.session_state['admin_auth'] = True
                    st.rerun()
                else:
                    st.error("❌ Wrong password!")
        return False
    return True


def _status_badge(active):
    if active:
        return '<span style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid #10b981; border-radius:4px; padding:1px 8px; font-size:10px; font-family:monospace;">ACTIVE</span>'
    return '<span style="background:rgba(100,116,139,0.15); color:#64748b; border:1px solid #64748b; border-radius:4px; padding:1px 8px; font-size:10px; font-family:monospace;">OFF</span>'


def _section_header(title, count, color="#00e5c3"):
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:space-between;
                    margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid #1e293b;">
            <div style="font-size:15px; font-weight:700; color:#e2e8f0;">{title}</div>
            <span style="background:rgba(0,229,195,0.1); color:{color};
                         border:1px solid rgba(0,229,195,0.2); border-radius:20px;
                         padding:2px 10px; font-size:11px; font-family:monospace;">
                {count} rules
            </span>
        </div>
    """, unsafe_allow_html=True)


def guardrails_admin_section():
    if not _check_auth():
        return

    st.markdown("""
        <div style="margin-bottom:8px;">
            <span style="background:rgba(239,68,68,0.1); color:#ef4444;
                         border:1px solid rgba(239,68,68,0.2); border-radius:20px;
                         padding:3px 12px; font-size:11px; font-family:monospace;
                         letter-spacing:1px;">🔐 ADMIN PANEL</span>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("⚙️ Dynamic Guardrails Manager")
    st.markdown("Rules yahan se add/edit/toggle karo — koi code change nahi chahiye!")

    col_logout, _ = st.columns([1, 4])
    with col_logout:
        if st.button("🚪 Admin Logout"):
            st.session_state['admin_auth'] = False
            st.rerun()

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🚫 Plan Exclusions",
        "👶 Age Restrictions",
        "⚠️ Prior Auth Triggers",
        "🔍 Fraud Signals"
    ])

    # ================================================================
    # TAB 1: PLAN EXCLUSIONS
    # ================================================================
    with tab1:
        exclusions = get_exclusions(active_only=False)
        _section_header("Plan Exclusions", len([e for e in exclusions if e[3]]))

        # Add new
        with st.expander("➕ Add New Exclusion"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_plan = st.selectbox("Insurance Plan", PLANS, key="excl_plan")
            with col_b:
                new_kw = st.text_input("Excluded Keyword", placeholder="e.g. cosmetic surgery", key="excl_kw")
            if st.button("Add Exclusion", key="add_excl"):
                if new_kw.strip():
                    add_exclusion(new_plan, new_kw.strip())
                    st.success(f"✅ Added: '{new_kw}' for {new_plan}")
                    st.rerun()
                else:
                    st.warning("Keyword empty hai!")

        st.markdown("")

        # Filter by plan
        filter_plan = st.selectbox("Filter by Plan:", ["ALL"] + PLANS, key="excl_filter")
        filtered = [e for e in exclusions if filter_plan == "ALL" or e[1] == filter_plan]

        # Display rules
        for rule in filtered:
            rid, plan, keyword, active = rule
            col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
            with col1:
                st.markdown(f"<span style='font-size:11px; color:#64748b;'>{plan}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(
                    f"<code style='background:#1e293b; color:#a5f3fc; padding:2px 8px; border-radius:4px;'>{keyword}</code> {_status_badge(active)}",
                    unsafe_allow_html=True
                )
            with col3:
                toggle_label = "Turn Off" if active else "Turn On"
                if st.button(toggle_label, key=f"toggle_excl_{rid}"):
                    toggle_exclusion(rid, 0 if active else 1)
                    st.rerun()
            with col4:
                if st.button("🗑️", key=f"del_excl_{rid}"):
                    delete_exclusion(rid)
                    st.rerun()

    # ================================================================
    # TAB 2: AGE RESTRICTIONS
    # ================================================================
    with tab2:
        age_rules = get_age_restrictions(active_only=False)
        _section_header("Age Restrictions", len([r for r in age_rules if r[5]]))

        with st.expander("➕ Add New Age Restriction"):
            col_a, col_b = st.columns(2)
            with col_a:
                ar_name = st.text_input("Condition Name", placeholder="e.g. Maternity", key="ar_name")
                ar_keywords = st.text_input("Keywords (comma separated)", placeholder="delivery,pregnancy,maternity", key="ar_kw")
            with col_b:
                ar_min = st.number_input("Min Age", 0, 120, 18, key="ar_min")
                ar_max = st.number_input("Max Age", 0, 120, 55, key="ar_max")
            ar_msg = st.text_input("Error Message", placeholder="Maternity covered age 18-55 only", key="ar_msg")
            if st.button("Add Age Rule", key="add_ar"):
                if ar_name and ar_keywords and ar_msg:
                    add_age_restriction(ar_name, ar_keywords, ar_min, ar_max, ar_msg)
                    st.success(f"✅ Added age restriction: {ar_name}")
                    st.rerun()
                else:
                    st.warning("Saare fields bharein!")

        st.markdown("")
        for rule in age_rules:
            rid, cname, keywords, min_age, max_age, message, active = rule
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.markdown(
                        f"**{cname}** {_status_badge(active)}<br>"
                        f"<span style='font-size:12px; color:#64748b;'>Age: {min_age}–{max_age} | Keywords: <code>{keywords[:50]}...</code></span><br>"
                        f"<span style='font-size:11px; color:#94a3b8;'>{message}</span>",
                        unsafe_allow_html=True
                    )
                with col2:
                    if st.button("Turn Off" if active else "Turn On", key=f"toggle_ar_{rid}"):
                        toggle_age_restriction(rid, 0 if active else 1)
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del_ar_{rid}"):
                        delete_age_restriction(rid)
                        st.rerun()
                st.markdown("<hr style='border-color:#1e293b; margin:8px 0;'>", unsafe_allow_html=True)

    # ================================================================
    # TAB 3: PRIOR AUTH TRIGGERS
    # ================================================================
    with tab3:
        pa_rules = get_prior_auth_triggers(active_only=False)
        _section_header("Prior Auth Triggers", len([r for r in pa_rules if r[2]]))

        with st.expander("➕ Add Prior Auth Trigger"):
            new_pa = st.text_input("Procedure/Keyword", placeholder="e.g. liver transplant", key="new_pa")
            if st.button("Add Trigger", key="add_pa"):
                if new_pa.strip():
                    add_prior_auth(new_pa.strip())
                    st.success(f"✅ Added PA trigger: '{new_pa}'")
                    st.rerun()
                else:
                    st.warning("Keyword empty hai!")

        st.markdown("")

        # Display in grid
        cols = st.columns(3)
        for i, rule in enumerate(pa_rules):
            rid, keyword, active = rule
            with cols[i % 3]:
                st.markdown(
                    f"<div style='background:#1e293b; border:1px solid #334155; border-radius:8px; "
                    f"padding:8px 12px; margin-bottom:8px;'>"
                    f"<code style='color:#a5f3fc;'>{keyword}</code> {_status_badge(active)}"
                    f"</div>",
                    unsafe_allow_html=True
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("On/Off", key=f"toggle_pa_{rid}"):
                        toggle_prior_auth(rid, 0 if active else 1)
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_pa_{rid}"):
                        delete_prior_auth(rid)
                        st.rerun()

    # ================================================================
    # TAB 4: FRAUD SIGNALS
    # ================================================================
    with tab4:
        fraud_rules = get_fraud_signals(active_only=False)
        _section_header("Fraud Signals", len([r for r in fraud_rules if r[4]]))

        with st.expander("➕ Add Fraud Signal"):
            fs_name = st.text_input("Signal Name", placeholder="e.g. Upcoding", key="fs_name")
            fs_kw = st.text_input("Trigger Keywords (comma separated)", placeholder="minor,simple,routine", key="fs_kw")
            fs_msg = st.text_area("Warning Message", placeholder="Potential upcoding detected...", key="fs_msg")
            if st.button("Add Fraud Signal", key="add_fs"):
                if fs_name and fs_kw and fs_msg:
                    add_fraud_signal(fs_name, fs_kw, fs_msg)
                    st.success(f"✅ Added fraud signal: {fs_name}")
                    st.rerun()
                else:
                    st.warning("Saare fields bharein!")

        st.markdown("")
        for rule in fraud_rules:
            rid, sname, keywords, message, active = rule
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(
                    f"**{sname}** {_status_badge(active)}<br>"
                    f"<span style='font-size:12px; color:#64748b;'>Keywords: <code>{keywords}</code></span><br>"
                    f"<span style='font-size:11px; color:#94a3b8;'>{message}</span>",
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("Turn Off" if active else "Turn On", key=f"toggle_fs_{rid}"):
                    toggle_fraud_signal(rid, 0 if active else 1)
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_fs_{rid}"):
                    delete_fraud_signal(rid)
                    st.rerun()
            st.markdown("<hr style='border-color:#1e293b; margin:8px 0;'>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("⚠️ Changes yahan se hote hi live ho jaate hain — koi restart nahi chahiye.")