"""Inspection UI for Cited's cited-answer API."""

import os
from collections import defaultdict

import requests
import streamlit as st

API_URL = os.getenv("CITED_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Cited", page_icon="*", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at 10% 16%, rgba(61,153,162,.20), transparent 23rem), radial-gradient(circle at 88% 4%, rgba(60,80,167,.26), transparent 29rem), #071019; color: #eaf6f7; font-family: 'Space Grotesk', sans-serif; }
    .stApp:before { background-image: radial-gradient(#afe9ee .7px, transparent .7px); background-size: 31px 31px; content: ''; inset: 0; opacity: .18; pointer-events: none; position: fixed; animation: drift 36s linear infinite; z-index: -1; }
    @keyframes drift { from { transform: translateY(0); } to { transform: translateY(-31px); } }
    .block-container { max-width: 980px; padding-top: 4.5rem; padding-bottom: 4rem; }
    .hero { margin-bottom: 2.4rem; } .eyebrow, .section-label { color: #afeeee; font: 500 .73rem 'DM Mono', monospace; letter-spacing: .16em; }
    .hero h1 { color: #f4fcfc; font-size: clamp(3rem, 9vw, 5.8rem); letter-spacing: -.08em; line-height: .86; margin: 0; }
    .hero p:last-child { color: #abc1c6; font-size: 1.08rem; max-width: 38rem; margin-top: 1.2rem; }
    [data-testid='stTextArea'] textarea { background: rgba(8,26,35,.82); border: 1px solid rgba(175,238,238,.32); border-radius: 12px; color: #f4fcfc; font-family: 'Space Grotesk', sans-serif; }
    [data-testid='stTextArea'] textarea:focus { border-color: #afeeee; box-shadow: 0 0 0 1px #afeeee; }
    .stButton > button, [data-testid='stFormSubmitButton'] > button, .stLinkButton > a { background: #afeeee; border: 0; border-radius: 999px; color: #07212a; font-family: 'DM Mono', monospace; font-weight: 500; padding: .62rem 1.15rem; }
    [data-testid='stFormSubmitButton'] > button:hover { background: #e6ffff; color: #041218; }
    .answer-card { background: rgba(10,28,37,.76); border: 1px solid rgba(175,238,238,.18); border-radius: 16px; padding: 1.25rem 1.35rem; }
    .answer-card p { color: #e7f5f5; font-size: 1.06rem; line-height: 1.7; margin-bottom: 0; } .section-label { margin: 2rem 0 .65rem; }
    [data-testid='stMetricValue'] { color: #afeeee; font-family: 'DM Mono', monospace; }
    </style>
    <div class="hero"><p class="eyebrow">RESEARCH, WITH RECEIPTS</p><h1>Cited<span style="color:#afeeee">.</span></h1><p>Ask the indexed research corpus. Every answer is grounded in retrieved evidence you can inspect in the original paper.</p></div>
    """,
    unsafe_allow_html=True,
)

with st.form("question_form"):
    query = st.text_area("Ask a research question", placeholder="How does SimCLR use data augmentation?", label_visibility="collapsed")
    submitted = st.form_submit_button("Follow the evidence ->", type="primary")

if submitted and query.strip():
    try:
        response = requests.post(f"{API_URL}/answer", json={"query": query}, timeout=120)
        response.raise_for_status()
        st.session_state["answer_data"] = response.json()
    except requests.RequestException as error:
        st.error(f"Could not reach the API: {error}")

data = st.session_state.get("answer_data")
if data:
    st.markdown("<p class='section-label'>CITED ANSWER</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='answer-card'><p>{data['answer']}</p></div>", unsafe_allow_html=True)
    if data["refused"]:
        st.info("The corpus did not contain enough reliable evidence for this question.")

    left, right = st.columns(2)
    left.metric("Retrieved", data["retrieved_count"], "hybrid candidates")
    right.metric("Reranked", data["reranked_count"], "evidence candidates")

    if data["citations"]:
        st.markdown("<p class='section-label'>EVIDENCE TRAIL</p>", unsafe_allow_html=True)
        citations_by_paper = defaultdict(list)
        for citation in data["citations"]:
            citations_by_paper[citation["doc_id"]].append(citation)

        for doc_id, citations in citations_by_paper.items():
            pages = sorted({citation["page_number"] for citation in citations})
            first_citation = citations[0]
            st.markdown(f"#### {doc_id}")
            st.caption(f"Cited pages: {', '.join(map(str, pages))}")
            st.link_button("Open paper", f"{API_URL}{first_citation['paper_path']}")

            by_page = {citation["page_number"]: citation for citation in citations}
            page_links = " | ".join(
                f"[Open page {page}]({API_URL}{citation['paper_path']})"
                for page, citation in sorted(by_page.items())
            )
            st.markdown(page_links)
            with st.expander("Show highlighted evidence"):
                for page, citation in sorted(by_page.items()):
                    st.caption(f"Page {page} | {citation['chunk_type']} | {citation['chunk_id']}")
                    st.image(f"{API_URL}{citation['highlight_path']}", caption="Paleturquoise marks the retrieved evidence text.")
            for citation in citations:
                if citation.get("source_image_path"):
                    st.image(citation["source_image_path"], caption="Original table crop")
            st.divider()
