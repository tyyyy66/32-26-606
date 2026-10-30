import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime
from datetime import timedelta
import requests
import re

# 1. 网页高级配置
st.set_page_config(page_title="我的专属聊天工具219", page_icon="32-26-606！💬", layout="wide")#串了哈哈哈

# 2. 连接 DeepSeek
try:
    client = OpenAI(
        api_key=st.secrets["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"#API不会再直接出现在code中，保密这一块（
    )
except Exception:
    st.error("🚨 警报：没找到 DeepSeek API Key，请去 Secrets 检查。")
    st.stop()

HISTORY_FILE = "history.json"#保存聊天记录
PROMPT_FILE = "prompt.json"  # 自动生成的“小本子”，用来记住你的提示词

# 3. 读取上一次保存的提示词（如果第一次运行，就用默认的）
default_prompt = "你是一个乐于助人的中文助手，回答简洁准确。"#给他的默认提示词
try:
    if os.path.exists(PROMPT_FILE):#判断这个小本子是不是存在的
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            saved_prompt = json.load(f)
            default_prompt = saved_prompt.get("prompt", default_prompt)#读取prompt的内容，如果没有的话，就使用那个默认提示词
except Exception:
    pass

# 4. 侧边栏与人设配置
with st.sidebar:
    st.title("💬 我的助手")

    custom_prompt = st.text_area("🎭 设置 AI 的人设（提示词）", value=default_prompt, height=200)
    try:
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            json.dump({"prompt": custom_prompt}, f, ensure_ascii=False)
    except Exception:
        pass

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
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                st.session_state.messages = json.load(f)
        except Exception:
            st.session_state.messages = []
    else:
        st.session_state.messages = []

# 7. 画出历史对话的气泡
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 8. 接收输入并回复
if prompt := st.chat_input("说点什么吧，爸爸（妈妈）..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):# 绑定左侧填写的提示词, 获取当前的北京时间
        search_result = ""#新增判断是否需要联网搜索

        if "?" in prompt or "？" in prompt or len(prompt) > 5:
            st.info(f"🌐 正在全网搜索关于“{prompt}”的最新情报...")

            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                search_url = "https://cn.bing.com/search"
                res = requests.get(
                    search_url,
                    params={"q": prompt},
                    headers=headers,
                    timeout=5
                )

                if res.status_code == 200:
                    titles = re.findall(r"<h2><a[^>]*>(.*?)</a></h2>", res.text)

                    if titles:
                        search_result = "【偷偷联网搜到的最新网页标题】：\n"
                        for title in titles[:3]:
                            clean_title = re.sub(r"<[^>]+>", "", title)
                            search_result += f"- {clean_title}\n"
            except Exception:
                search_result = "【尝试搜索但失败了】"

        try:
            # 北京时间为 UTC+8
            now = (
                datetime.utcnow() + timedelta(hours=8)
            ).strftime("%Y年%m月%d日 %H:%M")
        except Exception:
            now = "无法获取时间"

        # 把时间拼接到你的提示词后面，强制 AI 认清现实
        time_prompt = custom_prompt + f"\n\n【系统提示：当前的北京时间是 {now}。请以此时间为准，不要瞎猜。】"
        system_prompt = {"role": "system", "content": time_prompt}

        final_prompt = prompt + "\n\n" + search_result # 把搜到的新闻和问题拼起来

        # 发送请求，开启流式输出（字一个个蹦）
        try:
            # 当前用户消息已经加入聊天记录，所以这里替换最后一条用户消息，
            # 确保联网搜索结果能够真正发送给 AI
            history_messages = st.session_state.messages[-20:-1]
            current_user_message = {"role": "user", "content": final_prompt}

            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[system_prompt] + history_messages + [current_user_message], # 只带最近20条（10轮），节约token，毕竟我是个穷逼
                stream=True
            )

            def gen():
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            reply = st.write_stream(gen())
        except Exception as e:
            st.error(f"请求失败：{e}")
            reply = "【请求失败】"

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # 9. 自动保存聊天记录（加上防崩溃保护）
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"聊天记录保存失败：{e}")
