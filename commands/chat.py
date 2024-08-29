from rag import rag_query
import streamlit as st

# Custom Header Section
logo_path = "imgs/edb_new.png"
primary_color = "#FF4B33"
background_color = "#FFFFFF"

header_css = f"""
<style>
.header {{
    background-color: {background_color};
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
    st.image(logo_path, width=150)

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

def chat(args, model, device, tokenizer):
    while True:
        question = st.chat_input("Chat started. Type 'exit' to end the chat. Ask a question about the EDB blog authors:")

        if question.lower() == "exit":
            break

        answer = rag_query(tokenizer=tokenizer, model=model, device=device, query=question, topk=5)
    
        with st.chat_message("Human"):
          st.write(answer)
        # print(f"You Asked: {question}")
        # print(f"Answer: {answer}")

    print("Chat ended.")
