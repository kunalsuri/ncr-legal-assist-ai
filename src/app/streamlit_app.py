"""Streamlit frontend — General Chat + Legal Research (RAG) modes."""
from __future__ import annotations

import datetime

import streamlit as st

from src.config import load_config
from src.generation.ollama_client import (
    OllamaLLMClient,
    is_ollama_running,
    list_ollama_models,
)
from src.generation.prompts import (
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
    USER_TEMPLATE,
    format_sources,
)
from src.generation.verifier import verify_answer

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ncr-legal-assist · AI Lab",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
/* ── Chat bubbles ── */
[data-testid="stChatMessage"] {
    padding: 0.4rem 0;
}
[data-testid="stChatMessage"][data-testid="stChatMessage"] p {
    margin-bottom: 0.4rem;
}

/* ── Chat input pill ── */
[data-testid="stChatInput"] textarea {
    border-radius: 24px !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.95rem !important;
}

/* ── Tab strip ── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.3rem;
}
[data-testid="stTabs"] [role="tab"] {
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.35rem 1.1rem;
    border-radius: 8px 8px 0 0;
}

/* ── Sidebar pill badges ── */
.badge-online {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(74,222,128,0.15);
    color: #4ade80;
    border: 1px solid rgba(74,222,128,0.35);
    border-radius: 9999px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-offline {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(248,113,113,0.15);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.35);
    border-radius: 9999px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* ── Model chip on assistant messages ── */
.model-chip {
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 1px 6px;
    font-size: 0.68rem;
    font-family: monospace;
    color: #64748b;
}

/* ── Metric containers ── */
[data-testid="metric-container"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.5rem 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state defaults ─────────────────────────────────────────────────────

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

if "chat_system_prompt" not in st.session_state:
    st.session_state["chat_system_prompt"] = (
        "You are a helpful, knowledgeable AI assistant. "
        "Answer clearly and concisely. Think step-by-step when needed. "
        "If you are unsure about something, say so honestly."
    )

# ── Helpers ────────────────────────────────────────────────────────────────────


@st.cache_resource
def get_config_and_retriever():
    """Load config; retriever is wired at build-index time."""
    app_cfg = load_config()
    return app_cfg, None


def _ts() -> str:
    return datetime.datetime.now().strftime("%H:%M")


def _word_count(text: str) -> int:
    return len(text.split())


def _export_chat() -> str:
    lines: list[str] = [
        f"# Chat export — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]
    for msg in st.session_state["chat_messages"]:
        role = msg["role"].upper()
        ts = msg.get("timestamp", "")
        model_tag = f"  [{msg['model']}]" if msg.get("model") else ""
        lines.append(f"### {role}{model_tag}  ({ts})")
        lines.append(msg["content"])
        lines.append("")
    return "\n".join(lines)


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("#### ⚙️ Configuration")
    st.divider()

    cfg, retriever = get_config_and_retriever()
    ollama_url = cfg.ollama_base_url

    running = is_ollama_running(base_url=ollama_url)

    if running:
        st.markdown(
            '<span class="badge-online">● Ollama online</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        models = list_ollama_models(base_url=ollama_url)
        if models:
            default_idx = models.index(cfg.llm_model) if cfg.llm_model in models else 0
            selected_model: str | None = st.selectbox(
                "Model",
                models,
                index=default_idx,
                help="Active Ollama model used for all queries",
            )
        else:
            st.warning("No local models found.\n\n```\nollama pull llama3.2\n```")
            selected_model = None
    else:
        st.markdown(
            '<span class="badge-offline">✕ Ollama offline</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.error(
            f"Start Ollama:\n```\nollama serve\n```\nExpected at `{ollama_url}`",
        )
        selected_model = None

    st.divider()

    with st.expander("⚡ Generation settings", expanded=False):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=cfg.llm_temperature,
            step=0.05,
            help="Higher = more creative; lower = more deterministic",
        )
        max_tokens = st.number_input(
            "Max tokens",
            min_value=128,
            max_value=8192,
            value=cfg.llm_max_tokens,
            step=128,
        )

    with st.expander("💬 Chat system prompt", expanded=False):
        st.session_state["chat_system_prompt"] = st.text_area(
            "system_prompt_input",
            value=st.session_state["chat_system_prompt"],
            height=150,
            label_visibility="collapsed",
            help="Instructions prepended to every general-chat conversation",
        )
        if st.button("↺ Reset to default", use_container_width=True):
            st.session_state["chat_system_prompt"] = (
                "You are a helpful, knowledgeable AI assistant. "
                "Answer clearly and concisely. Think step-by-step when needed. "
                "If you are unsure about something, say so honestly."
            )
            st.rerun()

    st.divider()

    col_ref, col_clr = st.columns(2)
    with col_ref:
        if st.button("🔄 Refresh", use_container_width=True, help="Re-check Ollama status"):
            st.rerun()
    with col_clr:
        if st.button(
            "🗑️ Clear", use_container_width=True, help="Clear general-chat history"
        ):
            st.session_state["chat_messages"] = []
            st.rerun()

    st.caption(f"Endpoint: `{ollama_url}`")


# ── Main header ────────────────────────────────────────────────────────────────

st.markdown("## ⚖️ ncr-legal-assist · AI Lab")

tab_chat, tab_rag = st.tabs(["💬  General Chat", "📚  Legal Research (RAG)"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — General Chat
# ══════════════════════════════════════════════════════════════════════════════

with tab_chat:

    # ── Stats row ────────────────────────────────────────────────────────────
    n_turns = sum(1 for m in st.session_state["chat_messages"] if m["role"] == "user")
    total_words = sum(_word_count(m["content"]) for m in st.session_state["chat_messages"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Conversation turns", n_turns)
    m2.metric("Words exchanged", total_words)
    m3.metric("Active model", selected_model or "—")

    st.divider()

    # ── Message history ───────────────────────────────────────────────────────
    for hist_msg in st.session_state["chat_messages"]:
        avatar = "🧑" if hist_msg["role"] == "user" else "🤖"
        with st.chat_message(hist_msg["role"], avatar=avatar):
            st.markdown(hist_msg["content"])
            if hist_msg["role"] == "assistant" and (
                hist_msg.get("model") or hist_msg.get("timestamp")
            ):
                chip = (
                    f'<span class="model-chip">{hist_msg["model"]}</span>'
                    if hist_msg.get("model")
                    else ""
                )
                ts_str = hist_msg.get("timestamp", "")
                st.caption(f"{chip} {ts_str}".strip(), unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────────────────
    if selected_model is None:
        st.info(
            "🦙 Select a running Ollama model in the sidebar to start chatting.",
            icon="ℹ️",
        )
    else:
        if prompt := st.chat_input("Ask me anything…", key="general_chat_input"):

            # Append and show the user bubble immediately
            user_msg: dict = {"role": "user", "content": prompt, "timestamp": _ts()}
            st.session_state["chat_messages"].append(user_msg)
            with st.chat_message("user", avatar="🧑"):
                st.markdown(prompt)

            # Build full messages list (multi-turn)
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state["chat_messages"]
            ]

            # Stream the assistant response
            llm = OllamaLLMClient(
                model=selected_model,
                temperature=temperature,
                max_tokens=int(max_tokens),
                base_url=ollama_url,
            )

            with st.chat_message("assistant", avatar="🤖"):
                response_text = str(
                    st.write_stream(
                        llm.generate_stream(
                            system_prompt=st.session_state["chat_system_prompt"],
                            messages=history,
                        )
                    )
                )
                ts_now = _ts()
                chip = f'<span class="model-chip">{selected_model}</span>'
                st.caption(f"{chip} {ts_now}", unsafe_allow_html=True)

            # Persist assistant reply
            st.session_state["chat_messages"].append(
                {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": ts_now,
                    "model": selected_model,
                }
            )

    # ── Export ────────────────────────────────────────────────────────────────
    if st.session_state["chat_messages"]:
        st.divider()
        col_dl, _ = st.columns([1, 5])
        with col_dl:
            st.download_button(
                label="⬇️ Export chat",
                data=_export_chat(),
                file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Legal Research (RAG)
# ══════════════════════════════════════════════════════════════════════════════

with tab_rag:

    st.caption(
        "Research RAG over Indian legal primary sources. "
        "**Not legal advice.** See DISCLAIMER.md."
    )

    st.warning(
        "⚠️  This is a technical research project. No knowledge-base articles "
        "have been reviewed by a qualified lawyer. Output may be incomplete "
        "or incorrect. Verify against cited primary sources before relying "
        "on any information.",
        icon="⚠️",
    )

    query = st.text_area(
        "Your legal question",
        height=120,
        placeholder="e.g. What does the Transfer of Property Act say about notice to quit?",
    )

    search_disabled = selected_model is None
    if search_disabled:
        st.info("Select a running Ollama model in the sidebar to enable search.")

    if st.button("🔍 Search", type="primary", disabled=search_disabled) and query.strip():
        llm = OllamaLLMClient(
            model=selected_model,  # type: ignore[arg-type]  # guarded by disabled check
            temperature=temperature,
            max_tokens=int(max_tokens),
            base_url=ollama_url,
        )

        if retriever is None:
            st.info("Knowledge base is empty in this scaffold release. Showing refusal path:")
            st.markdown(REFUSAL_MESSAGE)
        else:
            with st.spinner("Retrieving sources…"):
                results, confident = retriever.retrieve(query, k=cfg.top_k)

            if not confident:
                st.warning("Low retrieval confidence.")
                st.markdown(REFUSAL_MESSAGE)
            else:
                user_prompt = USER_TEMPLATE.format(
                    query=query, formatted_sources=format_sources(results)
                )
                with st.spinner(f"Generating with **{selected_model}**…"):
                    answer = llm.generate(SYSTEM_PROMPT, user_prompt)

                retrieved_ids = {r.article_id for r in results}
                ok, fabricated = verify_answer(answer, retrieved_ids)

                if not ok:
                    st.error("Answer failed citation verification — suppressed.")
                    st.caption(f"Fabricated or missing citations: {fabricated}")
                    st.markdown(REFUSAL_MESSAGE)
                else:
                    st.markdown(answer)
                    with st.expander("📄 Retrieved sources"):
                        for r in results:
                            st.markdown(
                                f"**{r.article_title}** "
                                f"(`{r.article_id}`, rerank={r.rerank_score:.2f}, "
                                f"status={r.article_status})"
                            )
                            st.code(r.text[:600] + ("…" if len(r.text) > 600 else ""))

    st.divider()
    st.caption(
        "Sources: India Code · Delhi Government Legislative Department · "
        "Delhi High Court · NJDG.  "
        "Real legal problem? Call DSLSA helpline **1516**."
    )

