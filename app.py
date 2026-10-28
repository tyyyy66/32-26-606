import streamlit as st
from openai import OpenAI

# 1. 网页高级配置
st.set_page_config(page_title="我的专属聊天工具", page_icon="💬", layout="wide")

# 2. 从保险箱拿钥匙（绝不能在代码里写死你的 sk-xxx！）
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"], 
    base_url="https://api.deepseek.com"
)

# 3. 加入侧边栏（左边的高级感）
with st.sidebar:
    st.title("💬 我的助手")
    st.caption("基于 DeepSeek 大模型")
    # 加一个清空聊天记录的按钮
    if st.button("🗑 清空聊天记录", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. 页面主标题
st.title("我的专属聊天工具")

# 5. 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. 画出历史对话的气泡
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. 接收输入
if prompt := st.chat_input("说点什么吧..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # 开启流式输出（字一个个蹦）
        system_prompt = {"role": "system", "content": "你是一个严谨的助手。如果不知道最新的事情，或者不确定的信息，请直接回答‘我不知道，我无法联网查询实时新闻’，绝对不允许胡编乱造。"}
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[system_prompt] +st.session_state.messages,
            stream=True
        )
        
        def gen():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        reply = st.write_stream(gen())
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
