import base64
import datetime
import re
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st
from google import genai
from google.genai import errors as genai_errors


# ============================================================
# PAGE CONFIGURATION — STREAMLIT DEFAULT STYLING
# ============================================================
st.set_page_config(
    page_title="Student Registration & AI SQL Assistant",
    page_icon="🎓",
    layout="wide",
)

st.markdown(
    """
    <style>
    @keyframes pageFadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stAppViewContainer"] {
        background-color: var(--background-color, #ffffff);
        background-image: linear-gradient(
            135deg,
            color-mix(in srgb, var(--background-color, #ffffff) 96%, #1E3A8A 4%) 0%,
            color-mix(in srgb, var(--background-color, #ffffff) 96%, #2563EB 4%) 100%
        );
    }

    div[data-testid="stMainBlockContainer"] {
        color: var(--text-color, #262730);
        animation: pageFadeIn 500ms ease-out both;
    }

    div[data-testid="stMainBlockContainer"] h1 {
        text-align: center;
        background-image: linear-gradient(
            90deg,
            color-mix(in srgb, var(--text-color, #262730) 75%, #0F172A 25%) 0%,
            color-mix(in srgb, var(--text-color, #262730) 55%, #1E3A8A 45%) 55%,
            color-mix(in srgb, var(--text-color, #262730) 40%, #2563EB 60%) 100%
        );
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(165deg, #0F172A 0%, #1E3A8A 58%, #2563EB 100%);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] [data-testid="stImage"] img {
        border: 2px solid rgba(255, 255, 255, 0.55);
        border-radius: 18px;
        box-shadow: 0 12px 28px rgba(5, 18, 35, 0.3);
    }

    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] button {
        color: #ffffff !important;
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.65) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.35) !important;
        opacity: 1 !important;
    }

    button[data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    button[data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1E3A8A 100%) !important;
    }

    button[data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] button svg,
    button[data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] button svg {
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
        opacity: 1 !important;
    }

    .social-links {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin: 12px 0;
    }

    .social-links a {
        display: inline-flex;
        width: 42px;
        height: 42px;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        transition: transform 180ms ease, box-shadow 180ms ease;
    }

    .social-links a:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.2);
    }

    .social-links a:focus-visible {
        outline: 3px solid #38bdf8;
        outline-offset: 3px;
    }

    .social-links img {
        display: block;
        width: 23px;
        height: 23px;
        object-fit: contain;
    }

    .toc-list {
        display: grid;
        gap: 12px;
        margin: 12px 0 20px;
    }

    .toc-card {
        display: block;
        padding: 14px 16px;
        color: var(--text-color, #262730) !important;
        text-decoration: none !important;
        border: 0;
        border-radius: 14px;
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.14);
        transition: transform 180ms ease, box-shadow 180ms ease;
    }

    .toc-card--registration,
    .st-key-registration-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 91%, #2563EB 9%);
    }

    .toc-card--records,
    .st-key-records-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 91%, #14B8A6 9%);
    }

    .toc-card--gemini,
    .st-key-gemini-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 91%, #8B5CF6 9%);
    }

    .toc-card--manual,
    .st-key-manual-sql-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 91%, #F59E0B 9%);
    }

    .st-key-registration-section,
    .st-key-records-section,
    .st-key-gemini-section,
    .st-key-manual-sql-section,
    .st-key-footer-section,
    .st-key-hero-section,
    .st-key-about-project-section {
        padding: 22px;
        border: 1px solid color-mix(in srgb, var(--text-color, #262730) 12%, transparent);
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
    }

    .st-key-hero-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 93%, #2563EB 7%);
        text-align: center;
    }

    .st-key-hero-section [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }

    .st-key-about-project-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 93%, #14B8A6 7%);
    }

    .st-key-about-project-section [data-testid="stExpander"] {
        background: transparent;
        border: 0;
        box-shadow: none;
    }

    .st-key-footer-section {
        background: color-mix(in srgb, var(--secondary-background-color, #ffffff) 91%, #1E3A8A 9%);
        text-align: center;
    }

    .st-key-footer-section .social-links {
        justify-content: center;
    }

    .toc-card:hover {
        color: var(--text-color, #262730) !important;
        transform: translateY(-2px);
        box-shadow: 0 9px 22px rgba(15, 23, 42, 0.2);
    }

    .toc-card:focus-visible {
        outline: 3px solid #2563EB;
        outline-offset: 3px;
    }

    .toc-card strong,
    .toc-card span {
        display: block;
    }

    .toc-card span {
        margin-top: 3px;
        opacity: 0.78;
    }

    div[data-testid="stExpander"],
    div[data-testid="stForm"] {
        color: var(--text-color, #262730);
        background: var(--secondary-background-color, rgba(255, 255, 255, 0.72));
        border: 1px solid rgba(99, 102, 241, 0.16);
        border: 1px solid color-mix(
            in srgb,
            var(--text-color, #262730) 12%,
            transparent
        );
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(30, 41, 59, 0.06);
    }

    div[data-testid="stMetric"] {
        box-sizing: border-box;
        display: flex;
        min-height: 124px;
        height: 100%;
        flex-direction: column;
        justify-content: center;
        padding: 16px;
        color: var(--text-color, #262730);
        background: var(--secondary-background-color, rgba(255, 255, 255, 0.72));
        border: 1px solid color-mix(
            in srgb,
            var(--text-color, #262730) 12%,
            transparent
        );
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(30, 41, 59, 0.06);
    }

    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        min-height: 2.5rem;
        align-items: center;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        color: #ffffff;
        background: linear-gradient(110deg, #0F172A 0%, #1E3A8A 55%, #2563EB 100%);
        border: 0;
        border-radius: 10px;
        transition: filter 180ms ease, transform 180ms ease, box-shadow 180ms ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        color: #ffffff;
        filter: brightness(1.15);
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(30, 58, 138, 0.28);
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

social_profiles = [
    (
        "LinkedIn",
        "https://www.linkedin.com/in/i-aman-rajpoot/?isSelfProfile=true",
        "social-linkedin.png",
        "image/png",
    ),
    (
        "Instagram",
        "https://www.instagram.com/i.aman.rajpoot",
        "social-instagram.png",
        "image/png",
    ),
    (
        "Portfolio website",
        "https://iamanrajpoot.netlify.app/",
        "social-portfolio.svg",
        "image/svg+xml",
    ),
    (
        "Email Aman",
        "mailto:amanrajpoot101@gmail.com",
        "social-email.svg",
        "image/svg+xml",
    ),
    (
        "WhatsApp Aman",
        "https://wa.me/919873341139?text=Hi%20Aman",
        "social-whatsapp.png",
        "image/png",
    ),
    (
        "GitHub profile",
        "https://github.com/i-aman-rajpoot",
        "social-github.png",
        "image/png",
    ),
]
social_icon_dir = Path(__file__).parent / "images"
social_links_html = '<div class="social-links">' + "".join(
    (
        f'<a href="{url}" aria-label="{label}" title="{label}" '
        'target="_blank" rel="noopener noreferrer">'
        f'<img src="data:{media_type};base64,'
        f'{base64.b64encode((social_icon_dir / icon_name).read_bytes()).decode("ascii")}" '
        'alt=""></a>'
    )
    for label, url, icon_name, media_type in social_profiles
) + "</div>"

with st.sidebar:
    st.image(str(Path(__file__).parent / "images" / "PROFILE.jpeg"), width=180)
    st.subheader("Aman Rajpoot")
    st.write(
        "I'm a data professional with 9+ years of overall professional experience, "
        "including 5 years of hands-on experience in the data and technology domain. "
        "After transitioning my career toward data analytics, I've focused on Python, "
        "SQL, data projects, automation, and problem-solving through technology. I "
        "enjoy building practical solutions that turn raw data into actionable "
        "business insights."
    )
    st.markdown(social_links_html, unsafe_allow_html=True)

with st.container(key="hero-section"):
    st.title("🎓 Student Registration & AI SQL Assistant")
    _, thumbnail_col, _ = st.columns([1, 3, 1])
    with thumbnail_col:
        st.image(
            str(Path(__file__).parent / "images" / "Student Data Lab Workflow.png"),
            use_container_width=True,
        )
    st.markdown(
        """
        **A practical end-to-end data project:** capture student details, store them in
        Supabase/PostgreSQL, inspect the source records, and answer business questions
        using Gemini-generated SQL — or write SQL yourself.
        """
    )

with st.container(key="about-project-section"):
    with st.expander("📘 Project overview, learning objectives & architecture", expanded=True):
        st.markdown("### Why I chose to build this project")
        st.write(
            "I built this project to make the journey from a form submission to a useful, "
            "verifiable answer easy to understand. It combines Streamlit, Supabase "
            "(PostgreSQL), Gemini AI, GitHub, and Streamlit Community Cloud in one practical "
            "application."
        )
        st.write(
            "People can submit student details and see them in a dataframe alongside "
            "existing database records. They can then ask Gemini a business question, such "
            "as “Which students enrolled in Python?” Gemini uses the table schema to suggest "
            "a SQL query; users can review and run it, then inspect the result as a dataframe."
        )
        st.write(
            "The goal is to show how AI can translate business questions into SQL while "
            "helping people learn SQL and become confident writing queries themselves. "
            "Users can compare query results with the source records to validate the answer."
        )

        st.markdown("### Table of contents")
        st.markdown(
            """
            <nav class="toc-list" aria-label="Table of contents">
                <a class="toc-card toc-card--registration" href="#student-registration">
                    <strong>1. Student registration</strong>
                    <span>Enter and save student details</span>
                </a>
                <a class="toc-card toc-card--records" href="#student-source-records">
                    <strong>2. Student source records</strong>
                    <span>Inspect existing database rows</span>
                </a>
                <a class="toc-card toc-card--gemini" href="#gemini-ai-assistant">
                    <strong>3. Gemini AI assistant</strong>
                    <span>Convert a business question into SQL</span>
                </a>
                <a class="toc-card toc-card--manual" href="#write-sql-yourself">
                    <strong>4. Write SQL yourself</strong>
                    <span>Practice queries and inspect results</span>
                </a>
            </nav>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Technology stack")
        st.markdown(
            "- [**Streamlit**](https://streamlit.io/): user interface and dataframes\n"
            "- [**Supabase**](https://supabase.com/) / "
            "[**PostgreSQL**](https://www.postgresql.org/): persistent database\n"
            "- [**Gemini AI**](https://ai.google.dev/gemini-api/docs): "
            "natural-language-to-SQL assistance\n"
            "- [**GitHub**](https://github.com/i-aman-rajpoot/student-registration-streamlit): "
            "source-code repository\n"
            "- [**Streamlit Community Cloud**](https://streamlit.io/cloud): "
            "application hosting"
        )

        st.markdown("### Workflow")
        st.code(
            "Registration form → Supabase/PostgreSQL → Source records dataframe\n"
            "Business question → Gemini AI → Review SQL → Run query → Results dataframe\n"
            "                                   ↘ Write SQL yourself ↗",
            language="text",
        )
        _, workflow_col, _ = st.columns([1, 3, 1])
        with workflow_col:
            st.image(
                str(
                    Path(__file__).parent
                    / "images"
                    / "Student Registration to AI-Powered SQL Workflow.png"
                ),
                caption="Student registration to AI-powered SQL workflow",
                use_container_width=True,
            )
# ============================================================
# DATABASE AND SQL HELPERS
# ============================================================
def get_connection(read_only=False):
    conn = psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        connect_timeout=10,
        application_name="student_registration_ai_sql_app",
    )
    if read_only:
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout = '15s'")
    return conn


def load_sql_prompt():
    prompt_path = Path("prompts/sql_prompt.txt")
    if not prompt_path.exists():
        raise FileNotFoundError("Could not find prompts/sql_prompt.txt.")
    return prompt_path.read_text(encoding="utf-8")


def clean_sql(sql):
    sql = (sql or "").strip()
    sql = re.sub(r"^\s*```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```\s*$", "", sql)
    return sql.strip()


def validate_read_only_sql(sql):
    sql = clean_sql(sql)
    if not sql:
        return False, "Please enter a SQL query.", ""

    statement = sql[:-1].rstrip() if sql.endswith(";") else sql
    if ";" in statement:
        return False, "Only one SQL statement can be run at a time.", ""
    if not re.match(r"^(SELECT|WITH)\b", statement, flags=re.IGNORECASE):
        return False, "Only read-only SELECT queries (including CTEs) are allowed.", ""

    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|"
        r"CALL|DO|COPY|VACUUM|REFRESH|EXECUTE|PREPARE|DEALLOCATE|"
        r"PG_READ_FILE|PG_READ_BINARY_FILE|PG_LS_DIR|LO_IMPORT|LO_EXPORT)\b",
        flags=re.IGNORECASE,
    )
    if forbidden.search(statement):
        return False, "The query contains a restricted command or function.", ""
    if re.search(
        r"\bFOR\s+(UPDATE|SHARE|NO\s+KEY\s+UPDATE|KEY\s+SHARE)\b",
        statement,
        flags=re.IGNORECASE,
    ):
        return False, "Locking clauses are not allowed.", ""
    return True, "", statement


def run_read_only_query(sql):
    valid, message, safe_sql = validate_read_only_sql(sql)
    if not valid:
        raise ValueError(message)

    conn = get_connection(read_only=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(safe_sql)
            if cursor.description is None:
                raise ValueError("The query did not return a result set.")
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchmany(1001)

        if len(rows) > 1000:
            rows = rows[:1000]
            st.info("Showing the first 1,000 rows to keep the app responsive.")
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.rollback()
        conn.close()


def fetch_students():
    conn = get_connection(read_only=True)
    try:
        return pd.read_sql_query(
            """
            SELECT student_id, student_name, student_email, student_phone,
                   student_course, student_dob, created_at
            FROM students
            ORDER BY student_id DESC
            """,
            conn,
        )
    finally:
        conn.rollback()
        conn.close()


def generate_sql(question):
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    model_name = st.secrets.get("GEMINI_MODEL", "gemini-3.8-flash")
    response = client.models.generate_content(
        model=model_name,
        contents=(
            load_sql_prompt()
            + "\n\nReturn only one read-only PostgreSQL SELECT query. "
              "Do not include Markdown fences or explanatory text."
            + "\n\nUSER QUESTION:\n"
            + question
        ),
    )
    return clean_sql(response.text)


def render_query_runner(sql, key_prefix):
    valid, message, _ = validate_read_only_sql(sql)
    if not valid:
        st.error(message)
        return

    with st.expander("Review SQL before execution", expanded=True):
        st.code(sql, language="sql")

    if st.button("▶ Run query", key=f"{key_prefix}_run", type="primary"):
        try:
            with st.spinner("Executing read-only query..."):
                result = run_read_only_query(sql)
            st.session_state[f"{key_prefix}_result"] = result
            st.success("Query executed successfully.")
        except Exception as exc:
            st.error(f"Query execution failed: {exc}")

    result = st.session_state.get(f"{key_prefix}_result")
    if result is not None:
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric("Rows returned", f"{len(result):,}")
        metric_col2.metric("Columns returned", f"{len(result.columns):,}")
        st.dataframe(result, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇ Download results as CSV",
            data=result.to_csv(index=False).encode("utf-8"),
            file_name=f"{key_prefix}_results.csv",
            mime="text/csv",
            key=f"{key_prefix}_download",
        )


# ============================================================
# SECTION 1 — STUDENT REGISTRATION
# ============================================================
st.divider()
with st.container(key="registration-section"):
    st.header("1. 📝 Student Registration", anchor="student-registration")
    st.caption("Enter student details and save them to the database.")

    with st.form("student_registration_form", clear_on_submit=False):
        left_col, right_col = st.columns(2)
        with left_col:
            name = st.text_input("Full name *", placeholder="e.g. Aman Sharma")
            email = st.text_input("Email address *", placeholder="student@example.com")
            phone = st.text_input("Phone number", placeholder="10-digit phone number")
        with right_col:
            course = st.text_input("Course *", placeholder="e.g. Python")
            dob = st.date_input(
                "Date of birth",
                value=datetime.date(2000, 1, 1),
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today(),
            )
        submitted = st.form_submit_button("Save student record", type="primary", use_container_width=True)

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Full name is required.")
        if not email.strip() or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
            errors.append("Enter a valid email address.")
        if not course.strip():
            errors.append("Course is required.")
        if phone.strip() and not re.fullmatch(r"\+?\d[\d\s\-()]{7,18}", phone.strip()):
            errors.append("Check the phone number format.")

        if errors:
            for error in errors:
                st.warning(error)
        else:
            conn = None
            try:
                conn = get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO students
                            (student_name, student_email, student_phone, student_course, student_dob)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING student_id
                        """,
                        (name.strip(), email.strip(), phone.strip() or None, course.strip(), dob),
                    )
                    new_id = cursor.fetchone()[0]
                conn.commit()
                st.success(f"Student saved successfully. Student ID: {new_id}")
                st.session_state.pop("student_records_cache", None)
            except Exception as exc:
                if conn:
                    conn.rollback()
                st.error(f"Could not save student: {exc}")
            finally:
                if conn:
                    conn.close()


# ============================================================
# SECTION 2 — SOURCE RECORDS
# ============================================================
st.divider()
with st.container(key="records-section"):
    st.header("2. 📋 Student Source Records", anchor="student-source-records")
    st.caption(
        "Inspect existing database records. Use this section to verify the results returned by your SQL queries."
    )

    if st.button("↻ Refresh source records", key="refresh_students"):
        st.session_state.pop("student_records_cache", None)

    try:
        if "student_records_cache" not in st.session_state:
            st.session_state["student_records_cache"] = fetch_students()
        source_df = st.session_state["student_records_cache"].copy()

        search_term = st.text_input(
            "Search source records",
            placeholder="Search by student name, email, phone, or course",
            key="source_search",
        )
        filtered_df = source_df
        if search_term.strip():
            mask = source_df.astype(str).apply(
                lambda column: column.str.contains(search_term.strip(), case=False, na=False)
            ).any(axis=1)
            filtered_df = source_df.loc[mask]

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Total student records", f"{len(source_df):,}")
        metric2.metric(
            "Distinct courses",
            f"{source_df['student_course'].nunique() if 'student_course' in source_df.columns else 0:,}",
        )
        metric3.metric("Records shown", f"{len(filtered_df):,}")

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇ Download source records as CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="student_source_records.csv",
            mime="text/csv",
            key="source_csv_download",
        )
    except Exception as exc:
        st.error(f"Could not load student records: {exc}")
        st.caption("Check your database secrets, network access, and students table schema.")


# ============================================================
# SECTION 3 — GEMINI AI ASSISTANT
# ============================================================
st.divider()
with st.container(key="gemini-section"):
    st.header("3. 🤖 Gemini AI: Business Question to SQL", anchor="gemini-ai-assistant")
    st.caption(
        "Ask a question in plain English. Gemini proposes SQL; review it before running it."
    )

    example_questions = [
        "Choose an example question...",
        "Give me the students enrolled in Python",
        "Show the number of students in each course",
        "List the most recently registered students",
        "Show month-wise student registration counts",
    ]
    chosen_example = st.selectbox("Example questions", example_questions, key="example_question")
    default_question = "" if chosen_example == example_questions[0] else chosen_example
    question = st.text_area(
        "Your business question",
        value=default_question,
        placeholder="e.g. Give me the students enrolled in Python",
        height=90,
        key="business_question",
    )

    if st.button("✨ Generate SQL with Gemini", type="primary", key="generate_gemini_sql"):
        if not question.strip():
            st.warning("Enter a business question first.")
        else:
            try:
                with st.spinner("Gemini is generating SQL..."):
                    generated_sql = generate_sql(question.strip())
                st.session_state["generated_sql"] = generated_sql
                st.session_state["generated_sql_question"] = question.strip()
                valid, message, _ = validate_read_only_sql(generated_sql)
                if valid:
                    st.success("SQL generated. Review it below before execution.")
                else:
                    st.warning(f"The generated SQL needs review: {message}")
            except Exception as exc:
                if (
                    isinstance(exc, genai_errors.APIError)
                    and exc.code == 503
                    and exc.status == "UNAVAILABLE"
                ):
                    st.warning(
                        "Gemini is temporarily experiencing high demand. "
                        "Please refresh the page and try again in a moment."
                    )
                else:
                    st.error(f"Could not generate SQL: {exc}")
                    st.caption(
                        "Check GEMINI_API_KEY, GEMINI_MODEL, and prompts/sql_prompt.txt."
                    )

    if st.session_state.get("generated_sql"):
        if st.session_state.get("generated_sql_question"):
            st.caption(f"Question: {st.session_state['generated_sql_question']}")
        editable_generated_sql = st.text_area(
            "Generated SQL (you can edit it before running)",
            value=st.session_state["generated_sql"],
            height=160,
            key="generated_sql_editor",
        )
        render_query_runner(editable_generated_sql, "gemini_query")


# ============================================================
# SECTION 4 — MANUAL SQL EDITOR
# ============================================================
st.divider()
with st.container(key="manual-sql-section"):
    st.header("4. ⌨️ Write SQL Yourself", anchor="write-sql-yourself")
    st.caption(
        "Practice SQL directly against your students table. This editor only permits read-only queries."
    )

    with st.expander("View students table schema", expanded=True):
        schema_df = pd.DataFrame(
            [
                ("student_id", "Integer", "Student record identifier"),
                ("student_name", "Text", "Student full name"),
                ("student_email", "Text", "Email address"),
                ("student_phone", "Text", "Phone number"),
                ("student_course", "Text", "Course name"),
                ("student_dob", "Date", "Date of birth"),
                ("created_at", "Timestamp", "Registration timestamp"),
            ],
            columns=["Column", "Typical type", "Description"],
        )
        st.dataframe(schema_df, use_container_width=True, hide_index=True)
        st.caption("This is based on the column names in the current app. Confirm against your actual database schema.")

    manual_sql = st.text_area(
        "Your SQL query",
        value=st.session_state.get(
            "manual_sql_initial",
            "SELECT student_name, student_email, student_course\n"
            "FROM students\n"
            "WHERE LOWER(student_course) = 'python'\n"
            "ORDER BY student_name;",
        ),
        height=180,
        key="manual_sql_editor",
        help="Use one SELECT query. Results are capped at 1,000 rows.",
    )
    render_query_runner(manual_sql, "manual_query")


# ============================================================
# FOOTER
# ============================================================
st.divider()
with st.container(key="footer-section"):
    st.markdown("**Developed by Aman Rajpoot**")
    st.caption(
        "Student Registration & AI SQL Assistant · Streamlit + Supabase/PostgreSQL + Gemini AI · "
        "Learn how data is stored, understand SQL, and verify the answer yourself."
    )
    st.markdown(social_links_html, unsafe_allow_html=True)
