import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Lead Ops Dashboard", layout="wide")

# --- Initialize Session State ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "draft_email" not in st.session_state:
    st.session_state.draft_email = None
if "company_name" not in st.session_state:
    st.session_state.company_name = None
if "lead_score" not in st.session_state:
    st.session_state.lead_score = None
if "message" not in st.session_state:
    st.session_state.message = None
if "status_message" not in st.session_state:
    st.session_state.status_message = None

st.title("🤖 Lead Ops Agent")
st.markdown("Simulate an inbound lead submission below.")

# Display the status message at the top if it exists
if st.session_state.status_message:
    if "✅" in st.session_state.status_message:
        st.success(st.session_state.status_message)
    else:
        st.error(st.session_state.status_message)

    # Add a small button to clear it
    if st.button("Dismiss Message"):
        st.session_state.status_message = None
        st.rerun()

# --- Input Form ---
with st.form("lead_form"):
    text_input = st.text_area(
        "Paste Inbound Email/Form Text",
        height=100,
        placeholder="Hi, I'm Sarah from TechNova...",
    )
    submitted = st.form_submit_button("Process Lead")

if submitted and text_input:
    with st.spinner("Agent is extracting, enriching, and scoring..."):
        try:
            res = requests.post(f"{API_URL}/webhook/lead", json={"text": text_input})
            
            if res.status_code != 200:
                st.error(f"API Error {res.status_code}: {res.text}")
            else:
                data = res.json()

                if "error" in data:
                    st.error(f"Backend error: {data['error']}")

                elif data["status"] == "pending_approval":
                    st.session_state.thread_id = data["thread_id"]
                    st.session_state.draft_email = data["draft_email"]
                    st.session_state.company_name = data["company_name"]
                    st.session_state.lead_score = data["lead_score"]
                    st.session_state.message = None
                    st.session_state.status_message = None  # Clear old messages
                else:
                    st.session_state.message = data["message"]
                    st.session_state.thread_id = None
                    st.session_state.draft_email = None
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to backend: {e}")

if st.session_state.message:
    st.warning(st.session_state.message)

# --- Human Review Panel ---
if st.session_state.thread_id and st.session_state.draft_email:
    st.divider()
    st.subheader(f"⏸️ Human Review Required: {st.session_state.company_name}")
    st.info(f"**Lead Score:** {st.session_state.lead_score}/100")

    st.markdown("### Draft Email")
    st.text_area(
        "Review the draft below",
        value=st.session_state.draft_email,
        height=250,
        disabled=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve & Send", use_container_width=True, type="primary"):
            with st.spinner("Sending..."):
                res = requests.post(
                    f"{API_URL}/approve/{st.session_state.thread_id}",
                    json={"status": "approved"},
                )

                if res.status_code == 200:
                    data = res.json()
                    # Save success message to session state
                    st.session_state.status_message = (
                        f"✅ Email sent! Saved to CRM with ID: {data.get('crm_id')}"
                    )

                    # Clear the draft
                    st.session_state.thread_id = None
                    st.session_state.draft_email = None
                    st.rerun()
                else:
                    st.error(f"Failed to resume graph: {res.text}")

    with col2:
        if st.button("❌ Reject", use_container_width=True):
            with st.spinner("Rejecting..."):
                res = requests.post(
                    f"{API_URL}/approve/{st.session_state.thread_id}",
                    json={"status": "rejected"},
                )

                if res.status_code == 200:
                    # Save rejection message to session state
                    st.session_state.status_message = (
                        "❌ Lead rejected. Email discarded."
                    )

                    # Clear the draft
                    st.session_state.thread_id = None
                    st.session_state.draft_email = None
                    st.rerun()
                else:
                    st.error(f"Failed to resume graph: {res.text}")
