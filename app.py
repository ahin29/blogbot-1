import streamlit as st
import openai
from openai import OpenAI

# Set up the page
st.set_page_config(page_title="LinQMD Medical Blog Assistant", page_icon="🩺")
st.title("🩺 LinQMD Medical Blog Assistant")

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about blog topics, SEO keywords, or request content creation..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("Creating your medical content..."):
            try:
                client = get_openai_client()
                
                # Build conversation history for the prompt
                conversation_context = ""
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        conversation_context += f"Doctor: {msg['content']}\n"
                    else:
                        conversation_context += f"Assistant: {msg['content']}\n"
                
                # Add the current message
                conversation_context += f"Doctor: {prompt}\n"
                
                # Use the medical blog creation prompt
                response = client.responses.create(
                    prompt={
                        "id": "pmpt_68b0581784d88197ab4ce500a74d64ed03c4a458ed97a713",
                        "version": "2"
                    },
                    input=conversation_context
                )
                
                # Extract the bot response from the output
                if hasattr(response, 'output') and len(response.output) > 0:
                    output_message = response.output[0]
                    if hasattr(output_message, 'content') and len(output_message.content) > 0:
                        content_item = output_message.content[0]
                        if hasattr(content_item, 'text'):
                            bot_response = content_item.text
                        else:
                            bot_response = str(content_item)
                    else:
                        bot_response = "No content in output message"
                else:
                    bot_response = "No output in response"
                
                st.markdown(bot_response)
                
                # Add bot response to chat history
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please check your API key and try again.")

# Sidebar with basic instructions
with st.sidebar:
    st.header("Instructions")
    st.write("1. Ask for blog topics or SEO keywords")
    st.write("2. Request complete blog posts")
    st.write("3. Get medical content writing tips")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
