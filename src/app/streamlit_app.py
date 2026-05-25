"""Streamlit frontend. Research-mode framing throughout."""
from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.generation.llm_client import LLMClient
from src.generation.prompts import (
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
    USER_TEMPLATE,
    format_sources,
)
from src.generation.verifier import verify_answer


st.set_page_config(
    page_title="delhi-legal-assist (research)",
    page_icon="⚖️",
    layout="wide",
)


@st.cache_resource
def get_pipeline():
    # The full pipeline (retriever + reranker + LLM) is wired here.
    # In v0.1 the agent should generate a TODO stub that returns a dummy
    # retriever and a real LLMClient, so the UI runs against an empty KB
    # and exercises the refusal path end-to-end.
    cfg = load_config()
    llm = LLMClient(cfg.llm_endpoint, cfg.llm_model, cfg.llm_temperature, cfg.llm_max_tokens)
    return cfg, llm, None  # retriever wired up in build_index.py runtime


st.title("delhi-legal-assist")
st.caption(
    "Research RAG over Indian legal primary sources. "
    "**Not legal advice.** See DISCLAIMER.md."
)

st.warning(
    "⚠️ This is a technical research project. No knowledge-base articles "
    "have been reviewed by a qualified lawyer. Output may be incomplete "
    "or incorrect. Verify against cited primary sources before relying "
    "on any information."
)

cfg, llm, retriever = get_pipeline()

query = st.text_area("Your question", height=120, placeholder=
    "e.g. What does the Transfer of Property Act say about notice to quit?")

if st.button("Search", type="primary") and query.strip():
    if retriever is None:
        st.info("Knowledge base is empty in this scaffold release. "
                "Refusal path:")
        st.markdown(REFUSAL_MESSAGE)
    else:
        with st.spinner("Retrieving sources..."):
            results, confident = retriever.retrieve(query, k=cfg.top_k)

        if not confident:
            st.warning("Low retrieval confidence.")
            st.markdown(REFUSAL_MESSAGE)
        else:
            user_prompt = USER_TEMPLATE.format(
                query=query, formatted_sources=format_sources(results)
            )
            with st.spinner("Generating..."):
                answer = llm.generate(SYSTEM_PROMPT, user_prompt)
            retrieved_ids = {r.article_id for r in results}
            ok, fabricated = verify_answer(answer, retrieved_ids)
            if not ok:
                st.error("Answer failed citation verification. Suppressed.")
                st.caption(f"Fabricated or missing citations: {fabricated}")
                st.markdown(REFUSAL_MESSAGE)
            else:
                st.markdown(answer)
                with st.expander("Retrieved sources"):
                    for r in results:
                        st.markdown(
                            f"**{r.article_title}** "
                            f"(`{r.article_id}`, rerank={r.rerank_score:.2f}, "
                            f"status={r.article_status})"
                        )
                        st.code(r.text[:600] + ("..." if len(r.text) > 600 else ""))

st.divider()
st.caption(
    "Sources: India Code, Delhi Government Legislative Department, "
    "Delhi High Court, NJDG. "
    "If you have a real legal problem, call DSLSA helpline 1516."
)
