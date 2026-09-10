import os
import requests
import streamlit as st
from datetime import datetime

API_BASE_URL = os.getenv("API_URL", "http://api:8000")


def chatbot_ui():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    project_id = st.session_state.get("current_project_id")

    if not project_id:
        st.info("Please select or create a project from the sidebar to start chatting.")
        return

    st.divider()
    st.subheader(f"Chat with Project: {project_id}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 View Sources"):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(
                            f"**Source {idx}** (Score: {source.get('score', 'N/A'):.3f})"
                        )
                        st.markdown(
                            f"```\n{source.get('text', '')[:500]}...\n```"
                            if len(source.get("text", "")) > 500
                            else f"```\n{source.get('text', '')}\n```"
                        )

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/nlp/answer/{project_id}",
                        json={"question": prompt, "limit": 5},
                    )

                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer generated.")
                        sources = data.get("sources", [])

                        st.markdown(answer)

                        if sources:
                            with st.expander("📚 View Sources"):
                                for idx, source in enumerate(sources, 1):
                                    st.markdown(
                                        f"**Source {idx}** (Score: {source.get('score', 'N/A'):.3f})"
                                    )
                                    text = source.get("text", "")
                                    st.markdown(
                                        f"```\n{text[:500]}...\n```"
                                        if len(text) > 500
                                        else f"```\n{text}\n```"
                                    )

                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer, "sources": sources}
                        )
                    else:
                        error_msg = f"Error: {response.status_code} - {response.text}"
                        st.error(error_msg)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_msg}
                        )

                except requests.exceptions.ConnectionError:
                    error_msg = "Connection Error: Unable to reach the API server."
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    if st.session_state.messages and st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
