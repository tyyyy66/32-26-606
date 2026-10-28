import streamlit as st
from openai import OpenAI
import json
import os

# 1. 网页高级配置
st.set_page_config(page_title="我的专属聊天工具", page_icon="💬", layout="wide")

# 2. 连接 DeepSeek
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"], 
    base_url="https://api.deepseek.com"
)

# 3. 侧边栏与人设配置
with st.sidebar:
    st.title("💬 我的助手")
    
    # 🌟 人设输入框（把 KPL 梗写在这里！）
    custom_prompt = st.text_area(
        "🎭 设置 AI 的人设（提示词）", 
        value="你是一个乐于助人的中文助手，回答简洁准确。",
        height=200
    )
    
    st.caption("基于 DeepSeek 大模型")
    
    if st.button("🗑 清空聊天记录", use_container_width=True):
        st.session_state.messages = []
        # 同时删除本地保存的文件
        if os.path.exists("history.json"):
            os.remove("history.json")
        st.rerun()

# 4. 页面主标题
st.title("我的专属聊天工具")

# 5. 初始化聊天记录（带有本地记忆功能）
HISTORY_FILE = "history.json"
if "messages" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

# 6. 画出历史对话的气泡
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. 接收输入并回复
if prompt := st.chat_input("说点什么吧..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # 绑定左侧填写的提示词（不再覆盖）
        system_prompt = {"role": "system", "content": custom_prompt}
        
        # 发送请求，开启流式输出
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[system_prompt] + st.session_state.messages,
            stream=True
        )
        
        def gen():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        reply = st.write_stream(gen())
        
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # 8. 自动保存聊天记录到 JSON 文件
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
