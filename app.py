#!/usr/bin/env python3
"""
多AI协作可视化界面
基于Streamlit实现的聊天界面，用于对接ProjectManager
"""
import streamlit as st
from manager import ProjectManager
from rich.console import Console

# 初始化控制台，用于调试
console = Console()

# 页面配置
st.set_page_config(
    page_title="多AI协作工具",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 侧边栏
with st.sidebar:
    st.title("🤖 多AI协作工具")
    st.markdown("""
    **可视化界面**
    - 与ProjectManager直接对话
    - 实时查看任务规划
    - 追踪项目状态
    
    **使用说明**
    1. 在聊天框中输入您的需求
    2. 系统会自动拆解为具体任务
    3. 查看任务规划结果
    """)
    
    # 版本信息
    st.markdown("---")
    st.markdown("**版本**: 1.0.0")
    st.markdown("**模式**: 可视化界面")

# 主界面
st.title("💬 多AI协作聊天界面")

# 初始化会话状态
if "manager" not in st.session_state:
    st.session_state.manager = ProjectManager()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好！我是多AI协作工具的项目经理。请输入您的需求，我会将其拆解为具体的任务。"
        }
    ]

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
if prompt := st.chat_input("请输入您的需求..."):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 处理用户输入
    if prompt.lower() == "exit":
        response = "工具已退出，感谢使用！"
    else:
        # 调用ProjectManager进行任务规划
        with st.spinner("正在规划任务..."):
            try:
                tasks = st.session_state.manager.plan_tasks(prompt)
                
                if tasks:
                    # 构建响应
                    response = f"## 任务规划结果\n\n"
                    response += "我已经将您的需求拆解为以下任务：\n\n"
                    
                    for i, task in enumerate(tasks, 1):
                        response += f"### 任务 {i}\n"
                        response += f"**ID**: {task.get('id', 'N/A')}\n"
                        response += f"**描述**: {task['description']}\n"
                        response += f"**优先级**: {task.get('priority', 'medium')}\n\n"
                    
                    response += "这些任务已经添加到工作流中，可以通过命令行界面执行。"
                else:
                    response = "任务规划失败，请重试。"
                    
            except Exception as e:
                console.print(f"错误: {e}")
                response = f"处理需求时发生错误: {str(e)}"
    
    # 添加助手响应到历史
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 显示助手响应
    with st.chat_message("assistant"):
        st.markdown(response)

# 底部信息
st.markdown("---")
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("**提示**: 输入 'exit' 退出工具")
with col2:
    st.markdown("**命令行模式**: 运行 `python main.py`", unsafe_allow_html=True)
