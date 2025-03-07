import streamlit as st
import ollama  # ใช้ในการเชื่อมต่อกับโมเดล Ollama API
import time # ใช้สำหรับหน่วงเวลาในการแสดงผล
import json # ใช้ในการจัดการไฟล์ JSON สำหรับบันทึกประวัติแชท

class ChatbotBackend:
    def __init__(self, model_name): # สร้าง class สำหรับ backend ของ chatbot
        self.model_name = model_name # กำหนดชื่อโมเดลที่ใช้ในการสร้างคำตอบ

    def get_response(self, user_message, selected_topic):
        try:
            response_container = st.empty() # สร้าง container สำหรับแสดงผลข้อความ
            full_response = ""  #ตัวแปรเก็บข้อความทั้งหมดที่ตอบกลับ


            messages = [  # ข้อความที่ถูกส่งไปยังโมเดล
                {'role': 'user', 'content': user_message},
                {'role': 'system', 'contents': "You are an assistant. Speak only English and Thai."},
                {'role': 'system', 'contents': "Don't speak LaTeX."},
                {'role': 'system', 'contents': "Don't speak Chinese."}
            ]

            with st.spinner('กำลังประมวลผลคำถาม...'):
                # การเชื่อมต่อกับ Ollama API และการส่งข้อความแบบ stream
             for chunk in ollama.chat(model=self.model_name, messages=messages, stream=True):
                full_response += chunk["message"]["content"]
                response_container.markdown(     # แสดงข้อความตอบกลับ
                    f'<div class="message-wrapper assistant-wrapper">'
                    f'<img src="{st.session_state.bot_avatar}" class="avatar">'
                    f'<div class="chat-bubble assistant-message">{full_response}</div></div>',
                    unsafe_allow_html=True
                )

            return full_response
        except Exception as e:
            return f"Error: {str(e)}"


# ฟังก์ชันในการบันทึกประวัติลงไฟล์ JSON
def save_history_to_json():
    if "history" not in st.session_state:
        st.session_state.history = []  # กำหนดค่าเริ่มต้นให้เป็นลิสต์ว่างๆ

    # เก็บข้อความในไฟล์ JSON
    with open("history.json", "w") as f:
        json.dump(st.session_state.history, f)


# ฟังก์ชันในการอ่านประวัติจากไฟล์ JSON
def load_history_from_json():
    try:
        with open("history.json", "r") as f:
            st.session_state.history = json.load(f)
    except FileNotFoundError:
        st.session_state.history = []  # ถ้าไฟล์ไม่มี ก็เริ่มต้นเป็นลิสต์ว่าง

st.set_page_config(page_title="Meta inbox", page_icon="https://cdn.discordapp.com/attachments/888438876480356376/1346467985237213224/download.jpg?ex=67c84b87&is=67c6fa07&hm=0915cb0fb5ecfff66492f67b5622a7d042b6583c4248c0ef3c6d8019c04f7355&")

# แสดง Sidebar
with st.sidebar:
    st.markdown("""
        <style>
            .sidebar-title {
                font-size: 30px; /* ปรับขนาดของคำว่า Home */
                font-weight: bold;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">Home</div>', unsafe_allow_html=True)
    st.image(    # แสดงภาพใน Sidebar
        "https://cdn.discordapp.com/attachments/888438876480356376/1346807975209336914/image.png?ex=67cad9ab&is=67c9882b&hm=5b404b161e6809388fa9a28610629c9f84c22adec4eb6748c4ce40a410e0817f&",
        use_container_width=True)

    # ตั้งชื่อผู้ใช้
    user_name = st.text_input("Set a username", value=st.session_state.get("user_name", "user"), max_chars=20)
    st.session_state.user_name = user_name

    # อัปโหลดภาพโปรไฟล์
    uploaded_avatar = st.file_uploader("Choose a profile picture", type=["jpg", "jpeg", "png"])

    if uploaded_avatar:
        st.session_state.user_avatar = uploaded_avatar
    elif 'user_avatar' not in st.session_state:
        # ถ้ายังไม่มีภาพโปรไฟล์ตั้งค่า default
        st.session_state.user_avatar = "https://cdn.discordapp.com/attachments/888438876480356376/1346426109344092200/bot.jpg?ex=67cac787&is=67c97607&hm=d50dd2ed13dec78e59e177e11dff8b0419af65f6c1b9b35db814931425caeddd&"

    # เลือกหัวข้อการสนทนา
    topic = st.selectbox("Choose a topic (to get better answers)", ["Technology", "Sports", "Movies", "General"])
    st.session_state.selected_topic = topic

    load_history_from_json()    # โหลดประวัติจากไฟล์ JSON

    # สไตล์ CSS สำหรับประวัติการแชท
    history_css = """
        <style>
            .history-container {
                background-color: #2a2a2a;
                border: 2px solid #4d4d4d;
                padding: 15px;
                border-radius: 10px;
                max-height: 300px;
                overflow-y: auto;
            }
            .history-title {
                font-size: 24px;
                font-weight: bold;
                color: white;
                margin-bottom: 10px;
            }
            .history-item {
                background-color: #3e3e3e;
                color: white;
                padding: 10px;
                margin-bottom: 5px;
                border-radius: 5px;
                font-size: 16px;
                display: flex;
                align-items: center;
            }
            .history-item a {
                color: lightblue;
                text-decoration: none;
            }
            .history-item a:hover {
                text-decoration: underline;
            }
            .history-icon {
                width: 20px;
                height: 20px;
                margin-right: 10px;
            }
        </style>
    """

    st.markdown(history_css, unsafe_allow_html=True)

    st.markdown('<div class="history-title">📩 History</div>', unsafe_allow_html=True)  # แสดงหัวข้อ History


    # แสดงประวัติข้อความที่เคยแชท
    history_html = ""
    for i, msg in enumerate(st.session_state.history):
        history_html += f"""
            <div class="history-item">
                <img src="https://cdn.discordapp.com/attachments/849108734768316456/1346891153676697700/FB_IMG_1737828589545.jpg?ex=67c9d5a3&is=67c88423&hm=eba52d0e11af45cefa516e9295cbcd657b0b2e8bd1b2ff699b21b0f3aa4cbdaf&" style="width: 30px; height: 30px; border-radius: 50%; margin-right: 10px;"  />
                <a href='#{i}'>{msg}</a>
            </div>
        """

    st.markdown(history_html, unsafe_allow_html=True) # แสดงประวัติการแชท
    st.markdown('</div>', unsafe_allow_html=True)



#ปรับ Sidebar ให้ดูเด่นขึ้น
    sidebar_css = """
            <style>
                [data-testid="stSidebar"] {
                    background-color: #181818;
                    border-right: 2px solid #333;
                    padding: 15px;
                }
                .stRadio > label {
                    font-weight: bold;
                    color: white;
                }
                .stMarkdown {
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }
            </style>
        """
    st.markdown(sidebar_css, unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'title_shown' not in st.session_state:
    st.session_state.title_shown = True

if 'user_avatar' not in st.session_state:
    st.session_state.user_avatar = "https://cdn.discordapp.com/attachments/888438876480356376/1346426109344092200/bot.jpg?ex=67cac787&is=67c97607&hm=d50dd2ed13dec78e59e177e11dff8b0419af65f6c1b9b35db814931425caeddd&"

if 'bot_avatar' not in st.session_state:
    st.session_state.bot_avatar = "https://cdn.discordapp.com/attachments/888438876480356376/1346426140989984788/user.jpg?ex=67cac78f&is=67c9760f&hm=9f87b20c8ae5c2866a8d3257b4684ff5c7f87aca91323407c6f5d36f990c1fae&"

title_placeholder = st.empty()

if st.session_state.title_shown:
    title_placeholder.markdown(
        """
        <h1 style="text-align: center; color: #6A6AC7;">Bot Meta Inbox</h1>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
    <style>
        .chat-container {
            max-width: 600px;
            margin: auto;
            display: flex;
            flex-direction: column;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 20px;
            margin-bottom: 10px;
            max-width: 80%;
            word-wrap: break-word;
            display: inline-block;
        }
        .user-message {
            background-color: #0084ff;
            color: white;
            align-self: flex-end;
            text-align: right;
        }
        .assistant-message {
            background-color: #e4e6eb;
            color: black;
            align-self: flex-start;
            text-align: left;
        }
        .message-wrapper {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .user-wrapper {
            flex-direction: row-reverse;
        }
        .assistant-wrapper {
            flex-direction: row;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin: 5px;
        }
         
    </style>
""", unsafe_allow_html=True)

chatbot = ChatbotBackend(model_name="phi3")

 #แสดงข้อความในแชท (พร้อม ID)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, message in enumerate(st.session_state.messages):
    role_class = "user-message" if message['role'] == 'user' else "assistant-message"
    wrapper_class = "user-wrapper" if message['role'] == 'user' else "assistant-wrapper"
    avatar_url = st.session_state.user_avatar if message['role'] == 'user' else st.session_state.bot_avatar

    avatar_url = st.session_state.user_avatar if message['role'] == 'user' else st.session_state.bot_avatar

    st.markdown(
        f'<div id="{i}" class="message-wrapper {wrapper_class}"><img src="{avatar_url}" class="avatar"><div class="chat-bubble {role_class}">{message["content"]}</div></div>',
        unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

user_message = st.chat_input("Type something...") # ช่องกรอกข้อความของผู้ใช้
if user_message:
    # เพิ่มข้อความที่ผู้ใช้พิมพ์ลงในประวัติ
    st.session_state.history.append(user_message)

    # บันทึกประวัติลงในไฟล์ JSON
    save_history_to_json()

    title_placeholder.empty()
    st.session_state.title_shown = False

    st.session_state.messages.append({'role': 'user', 'content': user_message})
    st.markdown(
        f'<div class="message-wrapper user-wrapper"><img src="{st.session_state.user_avatar}" class="avatar"><div class="chat-bubble user-message">{user_message}</div></div>',
        unsafe_allow_html=True)

    time.sleep(2)  # รอ 2 วินาที

    typing_placeholder = st.empty()    # พื้นที่แสดงการพิมพ์ของแชทบอท
    answer = chatbot.get_response(user_message, st.session_state.selected_topic)   # เรียกใช้ฟังก์ชันเพื่อให้ chatbot ตอบกลับ
    st.session_state.messages.append({'role': 'assistant', 'content': answer})    # เพิ่มข้อความของแชทบอทลงในข้อความแชท
    typing_placeholder.empty()   # ลบพื้นที่แสดงการพิมพ์




