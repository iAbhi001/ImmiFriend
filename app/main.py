import streamlit as st
import os
from dotenv import load_dotenv

# Import our locked internal engine modules
from src.engine.search import get_context
from src.engine.auth import signed_request
from src.engine.prompt import get_system_prompt
from app.ui_styles import apply_styles, show_safety_banner

# Load environment variables (AWS Keys, etc.)
load_dotenv()

# --- 1. Page Configuration & UI ---
st.set_page_config(
    page_title="ImmiFriend AI", 
    page_icon="🤝", 
    layout="centered"
)

# Apply the friendly custom CSS and show the safety disclaimer
apply_styles()
show_safety_banner()

st.title("🤝 ImmiFriend")
st.markdown("*Your personal guide through the US immigration process.*")

# --- 2. Sidebar: Context & Reset ---
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.info(
        "I use official 2026 USCIS Policy Manuals and Form Instructions "
        "to provide you with accurate information."
    )

# --- 3. Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. Chat Input & Engine Execution ---
if prompt := st.chat_input("Ask me about filing fees, eligibility, or mailing addresses..."):
    
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # UI Placeholder for Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching official manuals..."):
            try:
                # A. Retrieve context using our Metadata-aware search
                # This returns (documents_list, metadatas_list)
                docs, metas = get_context(prompt)
                
                # B. Prepare the combined context string for the LLM
                context_text = "\n\n".join(docs)
                
                # C. Construct the prompt with our "Friend" persona logic
                system_message = get_system_prompt(context_text)
                
                # D. Build the direct API payload for Bedrock (Claude 3.5 Sonnet)
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "temperature": 0.2, # Lower temperature for higher factual accuracy
                    "system": system_message,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }

                # E. Call Bedrock directly via our DIY signed_request
                model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
                endpoint = f"{os.getenv('BEDROCK_ENDPOINT')}/model/{model_id}/invoke"
                
                response = signed_request("POST", endpoint, payload)
                
                if response.status_code == 200:
                    response_json = response.json()
                    answer = response_json['content'][0]['text']
                    
                    # Display the answer
                    st.markdown(answer)
                    
                    # F. Display the "Friend's Sources" for transparency
                    if metas:
                        sources = list(set([m['source'] for m in metas]))
                        source_links = f"**I found this in:** {', '.join(sources)}"
                        st.caption(source_links)
                    
                    # Store assistant message in history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                else:
                    st.error(f"Error calling the brain: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"I hit a snag: {str(e)}")