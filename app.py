import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 브랜딩 & 와이드 레이아웃 세팅] ---
st.set_page_config(
    page_title="Eco-Bot 챌린지", 
    page_icon="🌿", 
    layout="wide", # 양옆을 더 활용하기 위해 wide 모드 사용
    initial_sidebar_state="expanded"
)

# --- [2. AI 모델 자동 탐색 및 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def find_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(target)
    except: return None

model = find_working_model()

# --- [3. 스타일링 (양옆 배경 및 디자인)] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    
    /* 전체 배경색 및 폰트 */
    .stApp {
        background: linear-gradient(to right, #f0fdf4, #ffffff, #f0fdf4);
        font-family: 'Pretendard', sans-serif;
    }

    /* 상단 헤더 */
    .header-container {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 40px; border-radius: 25px;
        color: white; text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* 메인 카드 디자인 */
    .main-card {
        background: white; padding: 30px; border-radius: 20px;
        border: 1px solid #dcfce7; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* AI 가이드 박스 */
    .guide-box {
        background-color: #ecfdf5; border-left: 5px solid #10b981;
        padding: 20px; border-radius: 10px; color: #064e3b; font-size: 1.1em;
    }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [4. 사이드바 (양옆 허전함 채우기)] ---
with st.sidebar:
    st.image("https://img.freepik.com/free-vector/save-planet-concept-with-earth-recycling-symbol_23-2148520448.jpg", use_column_width=True)
    st.markdown("### 🌿 에코봇의 검사 기준")
    st.info("""
    1. **내용물:** 깨끗이 비웠나요?
    2. **라벨/뚜껑:** 다른 재질은 제거했나요?
    3. **부피:** 우유팩이나 박스는 **반드시 펼치거나 압착**했나요?
    4. **이물질:** 오염된 부분은 없나요?
    """)
    st.write("---")
    st.caption("대지고등학교 환경 프로젝트 팀")

# --- [5. 데이터 및 상태 관리] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [6. 메인 화면 로직] ---

# 화면 분할 (양옆에 AI 느낌의 에코 이미지를 배치)
col_left, col_main, col_right = st.columns([1, 3, 1])

with col_left:
    st.image("https://img.freepik.com/free-photo/vibrant-green-leaf-with-water-drops-symbolizing-nature-s-purity_911060-3940.jpg", caption="Nature Power")
    st.image("https://img.freepik.com/free-vector/flat-world-environment-day-illustration-with-planet-earth_23-2148924041.jpg")

with col_right:
    st.image("https://img.freepik.com/free-vector/flat-design-forest-landscape_23-2149155014.jpg", caption="Keep Clean")
    st.image("https://img.freepik.com/free-vector/organic-flat-world-environment-day-illustration_23-2148922573.jpg")

with col_main:
    st.markdown('<div class="header-container"><h1>🤖 Eco-Bot 챌린지</h1><p>깐깐한 AI의 분리배출 2단계 인증</p></div>', unsafe_allow_html=True)
    
    score = load_score()
    st.markdown(f"#### 🏆 우리 반 누적 점수: `{score}점`", unsafe_allow_html=True)

    # 1단계: 가이드 생성
    if st.session_state.step == 1:
        st.markdown('<div class="main-card"><h3>📸 1단계: 버리기 전 촬영</h3><p>쓰레기의 원래 상태를 보여주세요. AI가 배출 방법을 알려드립니다.</p></div>', unsafe_allow_html=True)
        img1 = st.camera_input("촬영하기", key="cam1")
        
        if img1:
            if st.button("배출 가이드 생성 💡"):
                with st.spinner("AI 분석 중..."):
                    try:
                        res = model.generate_content(["이 물건의 분리배출법을 알려줘. 특히 펼치기, 씻기, 라벨 제거 등 사용자가 '인증'할 때 지켜야 할 사항을 3가지로 강조해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    # 2단계: 깐깐한 인증
    elif st.session_state.step == 2:
        st.markdown(f'<div class="guide-box"><strong>📝 AI의 미션:</strong><br>{st.session_state.guide}</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="main-card"><h3>✅ 2단계: 실천 후 인증</h3><p>가이드대로 처리된 모습을 찍어주세요. <b>우유팩 펼치기, 라벨 제거 등</b>이 안 되어 있으면 반려됩니다!</p></div>', unsafe_allow_html=True)
        
        img2 = st.camera_input("인증샷 촬영", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("처음으로 돌아가기 🔄"):
                st.session_state.step = 1
                st.rerun()
        
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("깐깐한 AI 인증받기 ✅"):
                    with st.spinner("현미경 검사 중..."):
                        try:
                            # AI에게 깐깐한 검토 명령(Prompt Engineering)
                            verify_prompt = f"""
                            가이드: {st.session_state.guide}
                            사진 속 물체가 가이드대로 완벽하게 처리되었는지 검사해.
                            [검사 규칙]
                            1. 우유팩이나 종이 상자는 반드시 평평하게 '펼쳐져' 있어야 함. 접혀있거나 입체적이면 탈락.
                            2. 페트병은 라벨이 완전히 제거되어야 함.
                            3. 내용물이 비워지지 않고 지저분하면 탈락.
                            모든 조건이 완벽하면 '인증성공'이라는 단어를 넣고 칭찬해줘.
                            하나라도 부족하면 '인증실패'라고 말하고 부족한 점(예: 우유팩을 펼치지 않았습니다)을 아주 따갑게 혼내줘.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"⚠️ 인증 실패: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

        if st.session_state.verified:
            if st.button("다음 미션 수행하기 ➡️"):
                st.session_state.step = 1
                st.session_state.verified = False
                st.rerun()

st.markdown("---")
st.caption(f"접속 모델: {model.model_name if model else 'None'} | 대지고 환경 지킴이 시스템")
