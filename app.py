import streamlit as st
import openai
from openai import OpenAI

# Set up the page
st.set_page_config(
    page_title="LinQMD Medical Blog Assistant", 
    page_icon="🩺",
    layout="wide"
)

# Header with styling
st.title("🩺 LinQMD Medical Blog Creation Assistant")
st.markdown("### AI-Powered Blog Content Creator for Healthcare Professionals")
st.markdown("---")

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with doctor information and instructions
with st.sidebar:
    st.header("🏥 Doctor Information")
    
    # Optional: Collect doctor info for better personalization
    doctor_specialty = st.selectbox(
        "Medical Specialty:",
        ["General Practice", "Pediatrics", "OB/GYN", "ENT", "Cardiology", 
         "Endocrinology", "Dermatology", "Orthopedics", "Neurology", 
         "Psychiatry", "Other"]
    )
    
    doctor_location = st.text_input("Location (for local SEO):", placeholder="e.g., Bangalore, Mumbai")
    
    st.markdown("---")
    
    st.header("📝 How to Use")
    st.write("1. **Ask for blog topics**: 'Suggest blog topics for pediatrics'")
    st.write("2. **Request specific content**: 'Write a blog about childhood allergies'")
    st.write("3. **Get SEO keywords**: 'What are trending keywords for diabetes care?'")
    st.write("4. **Create full posts**: 'Create an SEO-optimized blog about hypertension'")
    
    st.markdown("---")
    
    st.header("✨ Features")
    st.write("• SEO-optimized content")
    st.write("• Medical compliance (NMC guidelines)")
    st.write("• Trending keyword integration")
    st.write("• Patient-friendly language")
    st.write("• Professional doctor voice")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"**Doctor:** {message['content']}")
            else:
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about blog topics, SEO keywords, or request content creation..."):
        # Add context about doctor's specialty if provided
        context_prompt = prompt
        if doctor_specialty and doctor_specialty != "Other":
            context_prompt = f"[Doctor Specialty: {doctor_specialty}] {prompt}"
        if doctor_location:
            context_prompt = f"[Location: {doctor_location}] {context_prompt}"
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"**Doctor:** {prompt}")
        
        # Generate AI response
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
                    
                    # Add the current message with context
                    conversation_context += f"Doctor: {context_prompt}\n"
                    
                    # Use the medical blog creation prompt
                    response = client.responses.create(
                        prompt={
                            "id": "pmpt_68b0581784d88197ab4ce500a74d64ed03c4a45",
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
                    
                    # Display the response
                    st.markdown(bot_response)
                    
                    # Add bot response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Please check your API configuration and try again.")

with col2:
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    
    if st.button("📋 Suggest Blog Topics"):
        quick_prompt = f"Suggest 5 trending blog topics for {doctor_specialty.lower()} that would rank well on SEO"
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()
    
    if st.button("🔍 Trending Keywords"):
        quick_prompt = f"What are the top trending SEO keywords for {doctor_specialty.lower()} in {doctor_location or 'India'}?"
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()
    
    if st.button("✍️ Write Sample Blog"):
        quick_prompt = f"Write a complete SEO-optimized blog post about a common condition in {doctor_specialty.lower()}"
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()
    
    if st.button("📊 SEO Tips"):
        quick_prompt = "Give me 10 SEO tips specifically for medical blogs that comply with NMC guidelines"
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 14px; margin-top: 20px;'>
        <p>🩺 <strong>LinQMD Medical Blog Assistant</strong> | AI-Powered Content Creation for Healthcare Professionals</p>
        <p>Built for medical compliance • SEO-optimized • Patient-focused content</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Display usage statistics
if st.session_state.messages:
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Session Stats")
    st.sidebar.write(f"Messages exchanged: {len(st.session_state.messages)}")
    st.sidebar.write(f"Specialty: {doctor_specialty}")
    if doctor_location:
        st.sidebar.write(f"Location: {doctor_location}")
