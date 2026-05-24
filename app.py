import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. API 및 AI 모델 자동 탐색 (에러 방어)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_working_model():
    """서버가 인식하는 최적의 모델을 자동으로 찾아 연결합니다."""
    try:
        # 사용 가능한 모델 목록을 조회하여 가장 적합한 flash 모델 선택
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in available_models if "1.5-flash" in m), None)
        if not target:
            target = next((m for m in available_models if "flash" in m), available_models[0])
        return genai.GenerativeModel(target)
    except Exception:
        # 리스트 조회 실패 시 가장 표준적인 이름 강제 시도
        return genai.GenerativeModel('gemini-1.5-flash')

model = get_working_model()

# --- [2. 이미지 로드 로직] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 디자인 세팅 (한글 폰트 + 정중앙 + 흰 막대 제거)] ---
st.set_page_config(page_title="자연의 연결", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    /* 예쁜 한글 폰트 불러오기 (고운 돋움, 블랙한산스) */
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Gowun+Dodum:wght@400;700&display=swap');

    /* 상단 흰색 막대 및 불필요한 요소 완전 제거 */
    header, [data-testid="stHeader"], .stDeployButton, footer {{
        visibility: hidden !important;
        display: none !important;
    }}
    .block-container {{padding-top: 2rem !important;}}

    /* 전체 배경: 고화질 숲 */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)),
                    url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* 모든 글씨: 흰색 + 검정 테두리 + 예쁜 한글 폰트 */
    h1, h2, h3, h4, p, span, label, .stMarkdown, div, .stCameraInput {{
        color: #ffffff !important;
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
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
             4px 4px 12px rgba(0,0,0,0.7) !important;
    }}

    /* 한글 메인 제목 스타일 */
    .main-title {{
        font-size: 5.5rem !important;
        font-family: 'Black Han Sans', sans-serif !important;
        margin-top: 10px !important;
        letter-spacing: -2px;
        color: #ffffff !important;
    }}

    .sub-title {{
        font-size: 1.4rem;
        letter-spacing: 5px;
        opacity: 0.9;
        margin-bottom: 40px;
    }}

    /* 에코룡 위치 및 말풍선 (왼쪽 하단 고정) */
    .mascot-container {{
        position: fixed;
        bottom: -60px; 
        left: -30px; 
        width: 400px;
        z-index: 999;
        pointer-events: none;
    }}
    .speech-bubble {{
        position: fixed;
        bottom: 440px; 
        left: 30px;   
        background: #ffffff;
        color: #059669 !important;
        padding: 18px 25px;
        border-radius: 35px;
        border: 4px solid #059669;
        font-weight: 700;
        font-size: 1.3rem;
        z-index: 1000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        text-shadow: none !important;
        text-align: left !important;
    }}

    /* 버튼 스타일: 깔끔하고 진한 초록 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 2px solid white !important;
        border-radius: 20px !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        height: 75px !important;
        width: 100% !important;
        text-shadow: none !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.4) !important;
    }}

    /* 카메라 입력창 테두리 */
    [data-testid="stCameraInput"] {{
        border: 4px solid #ffffff !important;
        border-radius: 20px !important;
        overflow: hidden;
    }}
    </style>
    
    <div class="speech-bubble">“우리의 작은 실천이<br>숲을 다시 숨쉬게 해요.” 🦖</div>
    <div class="mascot-container">
        <img src="{mascot_src}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [4. 점수 저장 로직] ---
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

# --- [5. 메인 UI 화면 (정중앙 정렬)] ---

# 제목
st.markdown('<h1 class="main-title">자연의 연결</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">에코 라이프 프로젝트</p>', unsafe_allow_html=True)

# 3단 컬럼을 활용한 중앙 집중형 레이아웃
col_empty_l, col_main, col_empty_r = st.columns([0.6, 3, 0.6])

with col_main:
    score = load_score()
    st.markdown(f"### 우리의 누적 실천 횟수: {score}")
    st.markdown("---")

    if not model:
        st.error("서버 연결에 실패했습니다. 페이지를 새로고침 해주세요.")
    else:
        # 1단계
        if st.session_state.step == 1:
            st.markdown("### 🔍 01. 대상 분석")
            st.write("분류가 필요한 자원을 카메라로 비춰주세요.")
            img1 = st.camera_input("", key="cam1")
            if img1:
                if st.button("분석 시작"):
                    with st.spinner("이미지를 식별하고 있습니다..."):
                        try:
                            res = model.generate_content(["이 물건의 분리배출 핵심 팁을 2줄로 알려줘.", Image.open(img1)])
                            st.session_state.guide = res.text
                            st.session_state.step = 2
                            st.rerun()
                        except Exception as e:
                            if "429" in str(e): st.error("🚨 사용량이 많습니다. 1분만 기다려주세요.")
                            else: st.error(f"오류: {e}")

        # 2단계
        elif st.session_state.step == 2:
            st.markdown(f"**🌱 AI 가이드:** {st.session_state.guide}")
            st.markdown("---")
            st.markdown("### ✨ 02. 실천 기록")
            st.write("가이드에 따라 분류된 모습을 촬영해주세요.")
            img2 = st.camera_input("", key="cam2")
            
            if img2 and not st.session_state.verified:
                if st.button("기록 완료"):
                    with st.spinner("기록을 검증하고 있습니다..."):
                        try:
                            # 깐깐한 조건 완화: 분류 시도 자체에 높은 점수
                            res = model.generate_content([f"가이드: {st.session_state.guide}. 잘 분류되었는지 확인해줘. 성공하면 반드시 '인증성공' 단어를 포함해줘.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("성공적으로 기록되었습니다!")
                            else:
                                st.error(f"확인 결과: {res.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            if st.button("다시 시도 🔄"):
                st.session_state.step = 1; st.rerun()

    if st.session_state.verified:
        if st.button("다음 기록 시작하기 ➡️"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

st.markdown("<p style='text-align:center; color:white; opacity:0.6; margin-top:60px;'>대지고등학교 환경 프로젝트 팀</p>", unsafe_allow_html=True)
