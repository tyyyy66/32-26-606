import streamlit as st
from openai import OpenAI

# 这里用 st.secrets 读取密钥，一会儿在 Streamlit 网页上填
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"], 
    base_url="https://api.deepseek.com"
)

st.title("💬 我的专属聊天工具")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("在这里输入你想说的话..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
