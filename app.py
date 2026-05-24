import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 기본 설정 및 AI 연결] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🦖", layout="wide")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(target)
    except: return None

model = get_model()

# --- [2. 깐깐한 디자인 & 고대비 가독성 CSS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@700;900&display=swap');

    /* 배경: 사용자 요청대로 고정 (숲 배경) + 가독성을 위해 어두운 필터 강화 */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                    url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 메인 카드: 흰색 빈 화면 느낌을 없애기 위해 패턴과 굵은 테두리 추가 */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        background-image: radial-gradient(#d1fae5 1px, transparent 1px);
        background-size: 20px 20px; /* 미세한 도트 패턴으로 빈 공간 채움 */
        border-radius: 40px;
        padding: 50px;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        margin: 40px auto;
        max-width: 900px;
        border: 8px solid #065f46; /* 굵은 초록색 테두리로 디자인 포인트 */
        position: relative;
    }

    /* 마스코트 에코룡 배치 (둘리 느낌의 공룡 캐릭터) */
    .mascot-box {
        position: fixed;
        bottom: 20px;
        left: 30px;
        width: 300px;
        z-index: 100;
    }
    .speech-bubble {
        position: fixed;
        bottom: 330px;
        left: 80px;
        background: #ffffff;
        color: #065f46;
        padding: 20px;
        border-radius: 30px;
        border: 4px solid #065f46;
        width: 250px;
        font-family: 'Pretendard', sans-serif;
        font-weight: 900;
        z-index: 101;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.1);
    }

    /* 텍스트 가독성: 배경 위에서도 잘 보이도록 그림자 효과 */
    .super-title {
        font-family: 'Black Han Sans', sans-serif;
        font-size: 5rem;
        color: #ffffff;
        text-align: center;
        text-shadow: 4px 4px 0px #065f46;
        margin-top: 50px;
    }
    
    .main-card-title {
        color: #064e3b;
        font-family: 'Pretendard', sans-serif;
        font-weight: 900;
        font-size: 2.2rem;
        border-bottom: 5px solid #10b981;
        display: inline-block;
        margin-bottom: 20px;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background: #065f46 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 20px !important;
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        width: 100% !important;
        box-shadow: 0 10px 0px #022c22 !important;
        transition: all 0.1s;
    }
    .stButton>button:active {
        transform: translateY(5px);
        box-shadow: 0 5px 0px #022c22 !important;
    }

    /* 점수판 */
    .score-board {
        position: fixed;
        top: 30px;
        right: 30px;
        background: #fde047;
        padding: 20px;
        border: 4px solid #000;
        border-radius: 20px;
        transform: rotate(5deg);
        font-family: 'Black Han Sans', sans-serif;
        font-size: 1.5rem;
    }
    </style>
    
    <!-- 마스코트: 에코룡 (초록 공룡) -->
    <div class="speech-bubble">거기 학생! <br>우유팩 안 펼치면 <br>국물도 없어! 🦖</div>
    <img src="https://cdn-icons-png.flaticon.com/512/2312/2312218.png" class="mascot-box">
    """, unsafe_allow_html=True)

# --- [3. 데이터 관리] ---
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

# --- [4. 화면 레이아웃] ---
score = load_score()
st.markdown(f'<div class="score-board">🏆 우리 반 점수: {score}점</div>', unsafe_allow_html=True)

st.markdown('<h1 class="super-title">Eco-Bot 챌린지</h1>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    if st.session_state.step == 1:
        st.markdown('<p class="main-card-title">📸 1단계: 버리기 전 사진</p>', unsafe_allow_html=True)
        st.write("### 에코룡에게 검사받을 물건을 보여주세요.")
        img1 = st.camera_input("카메라 실행", key="cam1")
        
        if img1:
            if st.button("에코룡아, 이거 어떻게 버려? 💡"):
                with st.spinner("에코룡이 깐깐하게 분석 중..."):
                    try:
                        prompt = "이 물건의 분리배출법을 한국어로 아주 깐깐하게 알려줘. 우유팩이라면 반드시 '펼쳐서 씻기'를 강조해."
                        res = model.generate_content([prompt, Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    elif st.session_state.step == 2:
        st.markdown('<p class="main-card-title">📝 에코룡의 특명</p>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background:#fff7ed; padding:25px; border-radius:20px; border:3px solid #ea580c; margin-bottom:20px; font-size:1.2rem; color:#7c2d12;">
                {st.session_state.guide}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<p class="main-card-title">✅ 2단계: 실천 인증샷</p>', unsafe_allow_html=True)
        st.write("### 가이드대로 안 했으면 올 생각도 마!")
        img2 = st.camera_input("인증 사진 촬영", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍을래 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("최종 확인 받기! ✅"):
                    with st.spinner("현미경으로 검사 중..."):
                        try:
                            verify_prompt = f"""
                            이전 가이드: {st.session_state.guide}
                            너는 깐깐한 공룡 감독관 '에코룡'이야. 
                            [검사 규칙]
                            1. 우유팩/종이상자: '반드시' 가위로 오려내어 평평하게 펼쳐진 상태여야 함. 조금이라도 입체적이면 무조건 탈락.
                            2. 라벨: 페트병 라벨이 1mm라도 남아있으면 탈락.
                            모든 조건이 완벽하면 '인증성공'이라 말해줘.
                            기준 미달이면 '인증실패'라고 말하고 학생을 아주 따갑게 혼내.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"🚫 판정 결과: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 쓰레기 가져오기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- [5. 푸터] ---
st.markdown("<p style='text-align:center; color:white; font-weight:bold;'>© 대지고 환경 프로젝트 | 에코룡은 지켜보고 있다.</p>", unsafe_allow_html=True)
