from rag import rag_query
from PIL import Image
import streamlit as st

# Custom Header Section
logo_path = "imgs/edb_new.png"
primary_color = "#FFFFFF"

header_css = f"""
<style>
.header {{
    padding: 10px;
    color: white;
}}
a {{
    color: {primary_color};
    padding: 0 16px;
    text-decoration: none;
    font-size: 16px;
}}
</style>
"""

st.markdown(header_css, unsafe_allow_html=True)

col1, col2 = st.columns([1, 4])

with col1:
    # st.image(logo_path, width=150)
    image = Image.open(logo_path)
    st.image(image)

with col2:
    st.markdown(
        f"""
    <div class="header">
        <a href="#" target="_blank">Products</a>
        <a href="#" target="_blank">Solutions</a>
        <a href="#" target="_blank">Resources</a>
        <a href="#" target="_blank">Company</a>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.title("RAG Application")

# Set up the session state to hold chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.messages.append({"role": "Assistant", "content": "Hello I'm a friendly bot that you can ask questions about authors in EDB blog."})
with st.chat_message("Assistant"):
    st.write(st.session_state.messages[0]["content"])
def chat(args, model_provider, model, device, tokenizer):
    # Function to handle sending a message and querying the model
    def send_message(user_input):
        
        if user_input.lower() == "exit":
            st.stop()  # End the chat if "exit" is typed

        
        # Append user's question to the chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Query the model for the answer
        answer = rag_query(tokenizer=tokenizer, model_provider=model_provider, model=model, device=device, query=user_input, topk=5, retriever_name=args.retriever_name)

        # Append model's answer to the chat history
        st.session_state.messages.append({"role": "bot", "content": answer})

        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("Human"):
                    st.write(message["content"])
            else:
                with st.chat_message("Assistant"):
                    st.write(message["content"])

    
    # Chat input box with unique key
    user_input = st.chat_input("Type your message here...")

    # If the user submits a message, process it
    if user_input:
        send_message(user_input)

