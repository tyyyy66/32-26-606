import streamlit as st
from openai import OpenAI

# 网页设置（这就是之前说的魔法 A，顺便加上了）
st.set_page_config(page_title="我的专属聊天工具", page_icon="💬")

client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"], 
    base_url="https://api.deepseek.com"
)

st.title("💬 我的专属聊天工具")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("在这里输入你想说的话..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # 🌟 这里就是魔法 C 的核心：开启流式输出
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,
            stream=True  # 告诉服务器：别等全生成完，生成一点发一点！
        )
        
        # 定义一个生成器，把蹦出来的字一个个接住
        def generate_chunks():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        # st.write_stream 会像打字机一样把字打出来，并返回完整的一句话
        reply = st.write_stream(generate_chunks())
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
