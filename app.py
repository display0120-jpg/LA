import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. API 및 AI 모델 자동 탐색 (404 해결 필살기)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_working_model():
    """서버 환경에 상관없이 작동하는 모델명을 자동으로 찾아 연결합니다."""
    try:
        # 1순위: 가장 표준적인 이름 시도
        m = genai.GenerativeModel('gemini-1.5-flash')
        m.generate_content("test") # 테스트 호출
        return m
    except:
        try:
            # 2순위: 사용 가능한 리스트 중 flash가 들어간 모델을 자동으로 매칭
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = next((m for m in available_models if "1.5-flash" in m), available_models[0])
            return genai.GenerativeModel(target)
        except:
            return None

model = get_working_model()

# --- [2. 이미지 로드 로직] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 디자인 세팅 (정중앙 + 가독성 + 흰색 막대 제거)] ---
st.set_page_config(page_title="에코룡의 지구 구출 작전", page_icon="🦖", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@900&display=swap');

    /* [필살기] 상단 흰색 막대, 푸터 완전 박멸 */
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

    /* [가독성 설정] 제목처럼 모든 글씨 흰색 + 두꺼운 검정 테두리 */
    h1, h2, h3, h4, p, span, label, .stMarkdown, div, .stCameraInput {{
        color: #ffffff !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 900 !important;
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
             4px 4px 10px rgba(0,0,0,0.7) !important;
    }}

    .main-title {{
        font-size: 5.5rem !important;
        font-family: 'Black Han Sans', sans-serif !important;
        margin-top: 20px !important;
        letter-spacing: -2px;
    }}

    .sub-title {{
        font-size: 1.5rem;
        letter-spacing: 10px;
        opacity: 0.9;
        margin-bottom: 50px;
    }}

    /* 에코룡 위치 조정 (살짝 왼쪽 아래) */
    .ecoryong-container {{
        position: fixed;
        bottom: -65px; 
        left: -30px; 
        width: 450px;
        z-index: 999;
        pointer-events: none;
    }}
    
    /* 말풍선 위치 조정 (왼쪽 위) */
    .speech-bubble {{
        position: fixed;
        bottom: 480px; 
        left: 20px;   
        background: #ffffff;
        color: #059669 !important;
        padding: 20px 30px;
        border-radius: 50px;
        border: 6px solid #059669;
        font-weight: 900 !important;
        font-size: 1.6rem;
        z-index: 1000;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.1);
        text-shadow: none !important;
        text-align: left !important;
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 4px solid white !important;
        border-radius: 30px !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        height: 100px !important;
        width: 100% !important;
        text-shadow: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important;
    }}

    /* 카메라 입력창 중앙 정렬 */
    [data-testid="stCameraInput"] {{
        margin: 0 auto !important;
        border: 4px solid #ffffff !important;
        border-radius: 30px !important;
        overflow: hidden;
    }}
    </style>
    
    <div class="speech-bubble">안녕! 난 지구 구출 대장<br>에코룡이야! 준비됐어? 🦖</div>
    <div class="ecoryong-container">
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

# --- [5. 메인 UI 화면 구성] ---

# 타이틀
st.markdown('<h1 class="main-title">에코룡의<br>지구 구출 작전</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">CIRCULAR LIFE PROJECT</p>', unsafe_allow_html=True)

# 3단 컬럼으로 중앙 정렬
col_l, col_main, col_r = st.columns([0.7, 3, 0.7])

with col_main:
    score = load_score()
    st.markdown(f"### 🏆 현재 우리 반 점수: {score}점")
    st.markdown("---")

    if not model:
        st.error("❌ 서버 연결 실패: 잠시 후 Reboot App을 실행해주세요.")
    else:
        # [설명글 복구] 1단계
        if st.session_state.step == 1:
            st.markdown("### 📸 1단계: 배출 전 상태 촬영")
            st.markdown("<p style='font-size:1.6rem;'>버리기 전의 상태를 에코룡에게 보여줘!</p>", unsafe_allow_html=True)
            img1 = st.camera_input("", key="cam1")
            if img1:
                if st.button("에코룡, 어떻게 버려? 💡"):
                    with st.spinner("에코룡이 분석 중..."):
                        try:
                            res = model.generate_content(["이 물건 분리배출법 3줄 요약해줘.", Image.open(img1)])
                            st.session_state.guide = res.text
                            st.session_state.step = 2
                            st.rerun()
                        except Exception as e:
                            st.error(f"오류: {e}")

        # [설명글 복구] 2단계
        elif st.session_state.step == 2:
            st.markdown(f"### 📝 에코룡의 지시사항")
            st.markdown(f"<p style='font-size:1.6rem;'>{st.session_state.guide}</p>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### ✅ 2단계: 실천 인증 촬영")
            st.markdown("<p style='font-size:1.6rem;'>가이드대로 정리했지? 제대로 안 하면 탈락이야!</p>", unsafe_allow_html=True)
            img2 = st.camera_input("", key="cam2")
            
            if img2 and not st.session_state.verified:
                if st.button("인증 완료! ✅"):
                    with st.spinner("현미경 검토 중..."):
                        try:
                            res = model.generate_content([f"가이드: {st.session_state.guide}. 잘 분류됐으면 '인증성공' 단어 포함해줘.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("성공적으로 기록되었습니다!")
                            else:
                                st.error(f"판정 결과: {res.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()

    if st.session_state.verified:
        if st.button("다음 작전 수행하기 ➡️"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

st.markdown("<p style='text-align:center; color:white; opacity:0.6; margin-top:100px; font-size:1.3rem;'>대지고등학교 환경 지킴이 | 캐릭터: 에코룡</p>", unsafe_allow_html=True)
