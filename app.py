import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. API 및 AI 모델 설정 (404 원천 차단)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_stable_model():
    """내 API 키로 사용 가능한 최적의 모델을 자동으로 찾아 연결합니다."""
    try:
        # 우선순위 1: 가장 안정적인 이름 시도
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        try:
            # 우선순위 2: 목록을 훑어서 'flash'가 포함된 모델 자동 선택
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                    return genai.GenerativeModel(m.name)
        except:
            return None

model = get_stable_model()

# --- [2. 이미지 로드 로직] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 정중앙 배치 & 극강 가독성 디자인 CSS] ---
st.set_page_config(page_title="Nature Connect", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');

    /* 상단 흰색 막대, 푸터 완전 제거 */
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

    /* [정중앙 정렬 + 흰색 글씨 + 검정 테두리] */
    h1, h2, h3, h4, p, span, label, .stMarkdown, div, .stCameraInput {{
        color: #ffffff !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 800 !important;
        text-align: center !important;
        text-shadow: 
            -3px -3px 0 #000,  
             3px -3px 0 #000,
            -3px  3px 0 #000,
             3px  3px 0 #000,
             0px -3px 0 #000,
             0px  3px 0 #000,
            -3px  0px 0 #000,
             3px  0px 0 #000,
             4px 4px 10px rgba(0,0,0,0.6) !important;
    }}

    .main-title {{
        font-size: 5.5rem !important;
        font-weight: 900;
        margin-top: 20px !important;
        letter-spacing: -2px;
    }}

    .sub-title {{
        font-size: 1.4rem;
        letter-spacing: 10px;
        opacity: 0.9;
        margin-bottom: 40px;
    }}

    /* 에코룡 위치 고정 */
    .mascot-box {{
        position: fixed;
        bottom: -50px;
        left: -30px;
        width: 380px;
        z-index: 1000;
        pointer-events: none;
    }}
    .speech-bubble {{
        position: fixed;
        bottom: 450px;
        left: 40px;
        background: rgba(255,255,255,0.95);
        padding: 20px 30px;
        border-radius: 30px;
        border: 4px solid #059669;
        font-weight: 800;
        color: #064e3b !important;
        text-shadow: none !important;
        z-index: 1001;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        text-align: left !important;
        max-width: 280px;
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 3px solid white !important;
        border-radius: 20px !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        height: 75px !important;
        width: 100% !important;
        text-shadow: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important;
    }}

    /* 카메라 입력창 중앙 정렬 */
    [data-testid="stCameraInput"] {{
        margin: 0 auto !important;
        border: 4px solid #ffffff !important;
        border-radius: 25px !important;
        overflow: hidden;
    }}
    </style>
    
    <div class="speech-bubble">“지구를 구하는 작은 기록,<br>제가 중앙에서 지켜볼게요!” 🦖</div>
    <div class="mascot-box">
        <img src="{mascot_src}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [4. 점수 관리 및 데이터] ---
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

# 타이틀
st.markdown('<h1 class="main-title">Nature Connect</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">CIRCULAR LIFE PROJECT</p>', unsafe_allow_html=True)

# 3단 컬럼으로 중앙 정렬 강제
col_l, col_center, col_r = st.columns([0.7, 3, 0.7])

with col_center:
    score = load_score()
    st.markdown(f"### CUMULATIVE IMPACT: {score}")
    st.markdown("---")

    if not model:
        st.error("❌ 서버 연결 실패: API 키를 확인하거나 Reboot App을 실행해주세요.")
    else:
        if st.session_state.step == 1:
            st.markdown("### 🔍 01. 대상 기록")
            st.write("순환이 필요한 자원을 카메라에 담아주세요.")
            img1 = st.camera_input("", key="cam1")
            if img1:
                if st.button("분석 엔진 가동"):
                    with st.spinner("이미지 식별 중..."):
                        try:
                            res = model.generate_content(["이 물건의 분리배출 팁을 2줄로 짧게.", Image.open(img1)])
                            st.session_state.guide = res.text
                            st.session_state.step = 2
                            st.rerun()
                        except Exception as e:
                            if "429" in str(e): st.error("🚨 사용자가 많습니다. 1분만 기다려주세요.")
                            else: st.error(f"오류: {e}")

        elif st.session_state.step == 2:
            st.markdown("### 🌱 AI 가이드")
            st.markdown(f"<p style='font-size:1.4rem;'>{st.session_state.guide}</p>", unsafe_allow_html=True)
            st.markdown("### ✨ 02. 가치 증명")
            st.write("분류가 완료된 실천의 모습을 촬영해주세요.")
            img2 = st.camera_input("", key="cam2")
            
            if img2 and not st.session_state.verified:
                if st.button("실천 기록하기"):
                    with st.spinner("검증 진행 중..."):
                        try:
                            res = model.generate_content([f"가이드: {st.session_state.guide}. 잘 분류됐으면 '인증성공' 단어 포함해줘.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("변화가 기록되었습니다!")
                            else: st.error(f"판정: {res.text}")
                        except Exception as e: st.error(f"Error: {e}")
            
            if st.button("처음으로"):
                st.session_state.step = 1; st.rerun()

    if st.session_state.verified:
        if st.button("새로운 순환 시작"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

st.markdown("<p style='text-align:center; color:white; opacity:0.6; margin-top:50px;'>Nature Connect Project | 대지고등학교</p>", unsafe_allow_html=True)
