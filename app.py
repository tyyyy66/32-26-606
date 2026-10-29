import streamlit as st
from openai import OpenAI
import json
import os

# 1. 网页高级配置
st.set_page_config(page_title="我的专属聊天工具219", page_icon="32-26-606！💬", layout="wide")#串了哈哈哈

# 2. 连接 DeepSeek
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"], 
    base_url="https://api.deepseek.com"#API不会再直接出现在code中，保密这一块（
)

HISTORY_FILE = "history.json"#保存聊天记录
PROMPT_FILE = "prompt.json"  # 自动生成的“小本子”，用来记住你的提示词

# 3. 读取上一次保存的提示词（如果第一次运行，就用默认的）
default_prompt = "你是一个乐于助人的中文助手，回答简洁准确。"#给他的默认提示词
if os.path.exists(PROMPT_FILE):#判断这个小本子是不是存在的
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        saved_prompt = json.load(f)
        default_prompt = saved_prompt.get("prompt", default_prompt)#读取prompt的内容，如果没有的话，就使用那个默认提示词

# 4. 侧边栏与人设配置
with st.sidebar:
    st.title("💬 我的助手")
    
    custom_prompt = st.text_area(
        "🎭 设置 AI 的人设（提示词）", 
        value=default_prompt, 
        height=200
    )
    
    # 🌟 如果你修改了框框里的词，立刻自动保存到文件里
    if custom_prompt != default_prompt:#判断提示词是否被修改
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            json.dump({"prompt": custom_prompt}, f, ensure_ascii=False)
            
    st.caption("基于 DeepSeek 大模型")
    
    if st.button("🗑 清空聊天记录", use_container_width=True):
        st.session_state.messages = []#清除聊天记录
        if os.path.exists(HISTORY_FILE):#判断聊天记录是否存在
            os.remove(HISTORY_FILE)
        st.rerun()#立即重新运行

# 5. 页面主标题
st.title("我的专属聊天工具219")

# 6. 初始化聊天记录（带有本地记忆功能）
if "messages" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

# 7. 画出历史对话的气泡
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 8. 接收输入并回复
if prompt := st.chat_input("说点什么吧爸爸（妈妈）..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        # 绑定左侧填写的提示词
        system_prompt = {"role": "system", "content": custom_prompt}
        
        # 发送请求，开启流式输出（字一个个蹦）
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
    
    # 9. 自动保存聊天记录
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
