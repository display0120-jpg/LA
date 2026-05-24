import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. API 및 AI 모델 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_stable_model():
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = get_stable_model()

# --- [2. 이미지 로드 로직] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 가독성 올인 디자인 (흰 막대 제거 + 화이트 텍스트 아웃라인)] ---
st.set_page_config(page_title="Nature Connect", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');

    /* [필살기 1] 상단 흰색 막대, 배포 버튼, 푸터 완전 박멸 */
    header, [data-testid="stHeader"], .stDeployButton, footer {{
        visibility: hidden !important;
        display: none !important;
    }}
    .block-container {{padding-top: 0rem !important;}}

    /* 배경: 고화질 숲 */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)),
                    url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* [필살기 2] 모든 글씨를 제목처럼! (흰색 글씨 + 진한 외곽선) */
    h1, h2, h3, h4, p, span, label, .stMarkdown, div {{
        color: #ffffff !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 800 !important;
        /* 8방향 텍스트 섀도우로 강력한 외곽선 형성 */
        text-shadow: 
            -2px -2px 0 #000,  
             2px -2px 0 #000,
            -2px  2px 0 #000,
             2px  2px 0 #000,
             0px -2px 0 #000,
             0px  2px 0 #000,
            -2px  0px 0 #000,
             2px  0px 0 #000,
             3px 3px 10px rgba(0,0,0,0.5) !important;
    }}

    /* 중앙 정렬용 레이아웃 크기 유지 */
    .main-wrapper {{
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }}

    .main-title {{
        font-size: 6rem !important;
        font-weight: 900;
        text-align: center;
        margin-top: 50px !important;
        letter-spacing: -2px;
    }}

    .sub-title {{
        font-size: 1.5rem;
        text-align: center;
        letter-spacing: 8px;
        opacity: 0.9;
        margin-bottom: 60px;
    }}

    /* 에코룡 위치 고정 */
    .mascot-box {{
        position: fixed;
        bottom: -50px;
        left: -30px;
        width: 400px;
        z-index: 1000;
        pointer-events: none;
    }}
    .speech-bubble {{
        position: fixed;
        bottom: 450px;
        left: 50px;
        background: rgba(255,255,255,0.9);
        padding: 20px 30px;
        border-radius: 30px;
        border: 4px solid #059669;
        font-weight: 800;
        color: #064e3b !important;
        text-shadow: none !important; /* 말풍선 안은 가독성을 위해 그림자 제거 */
        z-index: 1001;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}

    /* 버튼 스타일: 숲과 어울리는 진한 녹색 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 2px solid white !important;
        border-radius: 20px !important;
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        height: 80px !important;
        width: 100% !important;
        text-shadow: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
    }}

    /* 카메라 입력 가독성 */
    .stCameraInput {{
        border: 4px solid #ffffff !important;
        border-radius: 25px !important;
        overflow: hidden;
    }}
    </style>
    
    <div class="speech-bubble">“당신의 선한 영향력,<br>제가 끝까지 기록할게요!” 🦖</div>
    <div class="mascot-box">
        <img src="{mascot_src}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [4. 데이터 로직] ---
def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

# --- [5. 메인 UI 화면 구성] ---

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Nature Connect</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">CIRCULAR LIFE PROJECT</p>', unsafe_allow_html=True)

col_main, col_stat = st.columns([2.5, 1])

# 오른쪽 실시간 통계
with col_stat:
    score = load_score()
    st.markdown(f"""
        <div style="margin-top:20px;">
            <p style="font-size:1.1rem; opacity:0.8;">CUMULATIVE IMPACT</p>
            <h1 style="font-size:4.5rem; margin:0;">{score}</h1>
            <p style="margin-top:20px; font-size:0.9rem; line-height:1.6;">
                오늘의 메시지:<br>
                분리배출은 버리는 것이 아니라,<br>새로운 생명을 불어넣는 일입니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

# 중앙 메인 로직
with col_main:
    if st.session_state.step == 1:
        st.markdown("### 🔍 01. 대상 기록")
        st.write("순환이 필요한 자원을 카메라에 담아주세요.")
        img1 = st.camera_input("", key="cam1")
        if img1:
            if st.button("분석 엔진 가동"):
                with st.spinner("분석 중..."):
                    try:
                        res = model.generate_content(["이 물건의 분리배출 팁을 간결하게 2줄로.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    elif st.session_state.step == 2:
        st.markdown(f"**🌱 가이드:** {st.session_state.guide}")
        st.markdown("### ✨ 02. 가치 증명")
        st.write("분류가 완료된 실천의 모습을 증명해주세요.")
        img2 = st.camera_input("", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 시도"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("실천 기록"):
                    with st.spinner("검증 중..."):
                        try:
                            res = model.generate_content(["가이드대로 잘 분류되었는지 확인해줘. 성공하면 반드시 '인증성공' 단어 포함.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("기록 완료!")
                            else: st.error(f"판정: {res.text}")
                        except Exception as e: st.error(f"Error: {e}")

    if st.session_state.verified:
        if st.button("새로운 순환 시작"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
