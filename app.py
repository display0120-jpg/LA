import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. API 및 AI 모델 자동 탐색 (404 박멸 로직)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_stable_model():
    """서버 환경에 상관없이 작동하는 모델을 찾아 연결합니다."""
    try:
        # 가장 표준적인 이름부터 시도
        m = genai.GenerativeModel('gemini-1.5-flash')
        return m
    except:
        try:
            # 리스트 중 1.5-flash를 포함한 모델 자동 매칭
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = next((m for m in available if "1.5-flash" in m), available[0])
            return genai.GenerativeModel(target)
        except: return None

model = get_stable_model()

# --- [2. 이미지 로드 로직 (에코룡)] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 디자인 세팅 (정중앙 + 제목 글씨체 통일 + 흰 막대 제거)] ---
st.set_page_config(page_title="Nature Connect", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@900&display=swap');

    /* [상단 흰색 막대 및 푸터 완전 제거] */
    header, [data-testid="stHeader"], .stDeployButton, footer {{
        visibility: hidden !important;
        display: none !important;
    }}
    .block-container {{padding-top: 2rem !important;}}

    /* 전체 배경: 고화질 숲 */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)),
                    url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* [전체 글씨체 통일] 흰색 글씨 + 두꺼운 검정 테두리 */
    h1, h2, h3, h4, p, span, label, .stMarkdown, div, .stCameraInput {{
        color: #ffffff !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 900 !important;
        text-align: center !important;
        text-shadow: 
            -3px -3px 0 #000,  
             3px -3px 0 #000,
            -2px  2px 0 #000,
             2px  2px 0 #000,
             0px -3px 0 #000,
             0px  3px 0 #000,
            -3px  0px 0 #000,
             3px  0px 0 #000,
             5px 5px 15px rgba(0,0,0,0.7) !important;
    }}

    .main-title {{
        font-size: 6rem !important;
        font-family: 'Black Han Sans', sans-serif !important;
        margin-top: 0px !important;
        letter-spacing: -2px;
    }}

    .sub-title {{
        font-size: 1.5rem;
        letter-spacing: 12px;
        opacity: 0.9;
        margin-bottom: 40px;
    }}

    /* 에코룡 및 말풍선 위치 (요청하신 왼쪽 위/아래) */
    .mascot-container {{
        position: fixed;
        bottom: -65px; 
        left: -30px; 
        width: 420px;
        z-index: 999;
        pointer-events: none;
    }}
    
    .speech-bubble {{
        position: fixed;
        bottom: 480px; 
        left: 20px;   
        background: #ffffff;
        color: #059669 !important;
        padding: 20px 30px;
        border-radius: 40px;
        border: 5px solid #059669;
        font-weight: 900 !important;
        font-size: 1.5rem;
        z-index: 1000;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.1);
        text-shadow: none !important;
        text-align: left !important;
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 3px solid white !important;
        border-radius: 20px !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        height: 80px !important;
        width: 100% !important;
        text-shadow: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important;
    }}

    /* 카메라 입력창 디자인 */
    [data-testid="stCameraInput"] {{
        border: 5px solid white !important;
        border-radius: 30px !important;
        overflow: hidden;
    }}
    </style>
    
    <div class="speech-bubble">“오늘도 자연을 위한<br>작은 기록을 시작할까요?” 🦖</div>
    <div class="mascot-container">
        <img src="{mascot_src}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [4. 점수 및 상태 로직] ---
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

# --- [5. 메인 UI 구성 (정중앙 정렬)] ---

# 제목 섹션
st.markdown('<h1 class="main-title">Nature Connect</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">CIRCULAR LIFE PROJECT</p>', unsafe_allow_html=True)

# 3단 레이아웃으로 중앙 집중
col_l, col_main, col_r = st.columns([0.7, 3, 0.7])

with col_main:
    score = load_score()
    st.markdown(f"### CUMULATIVE IMPACT: {score}")
    st.markdown("---")

    if not model:
        st.error("❌ AI 연결 오류. 잠시 후 Reboot App을 시도해주세요.")
    else:
        # [간결한 설명글] 1단계
        if st.session_state.step == 1:
            st.markdown("### 🔍 01. 대상 기록")
            st.write("순환이 필요한 자원을 카메라에 담아주세요.")
            img1 = st.camera_input("", key="cam1")
            if img1:
                if st.button("분석 엔진 가동"):
                    with st.spinner("이미지 식별 중..."):
                        try:
                            res = model.generate_content(["이 물건 분리배출 팁을 2줄로 짧게.", Image.open(img1)])
                            st.session_state.guide = res.text
                            st.session_state.step = 2
                            st.rerun()
                        except Exception as e: st.error(f"오류: {e}")

        # [간결한 설명글] 2단계
        elif st.session_state.step == 2:
            st.markdown(f"**🌱 AI 가이드:** {st.session_state.guide}")
            st.markdown("---")
            st.markdown("### ✨ 02. 가치 증명")
            st.write("분류가 완료된 실천의 모습을 촬영해주세요.")
            img2 = st.camera_input("", key="cam2")
            
            if img2 and not st.session_state.verified:
                if st.button("실천 기록하기"):
                    with st.spinner("가치를 검증하고 있습니다..."):
                        try:
                            res = model.generate_content([f"가이드: {st.session_state.guide}. 잘 분류됐으면 '인증성공' 단어 포함해줘.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("변화가 기록되었습니다!")
                            else: st.error(f"판정: {res.text}")
                        except Exception as e: st.error(f"Error: {e}")
            
            if st.button("다시 시도 🔄"):
                st.session_state.step = 1; st.rerun()

    if st.session_state.verified:
        if st.button("새로운 순환 시작 ➡️"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

st.markdown("<p style='text-align:center; color:white; opacity:0.6; margin-top:80px;'>Nature Connect Project | 대지고등학교</p>", unsafe_allow_html=True)
