import streamlit as st
from src.engine.search import get_context
from src.engine.auth import signed_request
from src.engine.prompt import get_system_prompt
import os

st.set_page_config(page_title="ImmiFriend", page_icon="🤝")
st.title("🤝 ImmiFriend: Your Immigration Companion")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help with your visa today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Get Context
    docs, meta = get_context(prompt)
    context_str = "\n".join(docs)
    
    # 2. Build Payload
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": get_system_prompt(context_str),
        "messages": [{"role": "user", "content": prompt}]
    }

    # 3. Call Bedrock
    model_url = f"{os.getenv('BEDROCK_ENDPOINT')}/model/anthropic.claude-3-5-sonnet-20240620-v1:0/invoke"
    with st.chat_message("assistant"):
        response = signed_request("POST", model_url, payload)
        answer = response.json()['content'][0]['text']
        st.markdown(answer)
        st.caption(f"Sources: {', '.join(set([m['source'] for m in meta]))}")
    
    st.session_state.messages.append({"role": "assistant", "content": answer})