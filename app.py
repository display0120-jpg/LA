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
        # 모델명은 가장 안정적인 gemini-1.5-flash 사용
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = get_model()

# --- [2. 역대급 가독성 & 오리지널 캐릭터 CSS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@700;900&display=swap');

    /* 배경: 숲 배경 + 가독성을 위해 전체적으로 어두운 필터(Overlay)를 강하게 적용 */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 메인 카드: 가독성을 위해 완전 불투명한 흰색 배경 사용 */
    .main-container {
        background: #ffffff;
        border-radius: 40px;
        padding: 50px;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        margin: 40px auto;
        max-width: 850px;
        border: 10px solid #059669; /* 진한 초록색 테두리 */
        position: relative;
    }

    /* 에코룡 캐릭터 (2D 일러스트 스타일 고정 배치) */
    .mascot-container {
        position: fixed;
        bottom: 0px;
        left: 20px;
        width: 350px;
        z-index: 100;
        pointer-events: none; /* 클릭 방해 금지 */
    }
    
    .speech-bubble {
        position: fixed;
        bottom: 350px;
        left: 80px;
        background: #fde047; /* 노란색 말풍선으로 시선 집중 */
        color: #000000;
        padding: 20px 30px;
        border-radius: 30px;
        border: 4px solid #000000;
        font-family: 'Pretendard', sans-serif;
        font-weight: 800;
        font-size: 1.3rem;
        z-index: 101;
        box-shadow: 8px 8px 0px rgba(0,0,0,0.2);
    }

    /* 텍스트 가독성 최우선 설정 */
    .super-title {
        font-family: 'Black Han Sans', sans-serif;
        font-size: 5rem;
        color: #ffffff;
        text-align: center;
        text-shadow: 4px 4px 0px #059669; /* 제목 테두리 효과 */
        margin-top: 30px;
        letter-spacing: -2px;
    }

    .card-title {
        color: #064e3b;
        font-family: 'Pretendard', sans-serif;
        font-weight: 900;
        font-size: 2.2rem;
        margin-bottom: 20px;
        display: inline-block;
        border-bottom: 8px solid #10b981;
    }

    /* 카드 내부 모든 글씨를 진하게 처리하여 가독성 확보 */
    .info-text {
        color: #000000 !important;
        font-size: 1.4rem;
        line-height: 1.6;
        font-weight: 800;
        margin-bottom: 20px;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background: #059669 !important;
        color: #ffffff !important;
        border: 4px solid #000000 !important;
        border-radius: 20px !important;
        padding: 20px !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        width: 100% !important;
        box-shadow: 0 10px 0px #022c22 !important;
        transition: all 0.1s;
    }
    .stButton>button:active {
        transform: translateY(5px);
        box-shadow: 0 5px 0px #022c22 !important;
    }

    /* 점수판 디자인 */
    .score-badge {
        position: fixed;
        top: 30px;
        right: 40px;
        background: #fde047;
        color: #000;
        padding: 20px 40px;
        border: 5px solid #000;
        border-radius: 20px;
        font-family: 'Black Han Sans', sans-serif;
        font-size: 2rem;
        transform: rotate(3deg);
        z-index: 100;
    }
    </style>
    
    <!-- 캐릭터: 에코룡 (2D 공룡 캐릭터 일러스트) -->
    <div class="speech-bubble">거기 너!<br>우유팩 안 펼치면<br>에코룡이 혼낸다! 🦖</div>
    <div class="mascot-container">
        <!-- 실제 2D 일러스트 느낌의 공룡 캐릭터 사용 -->
        <img src="https://cdni.iconscout.com/illustration/premium/thumb/cute-dinosaur-illustration-download-in-svg-png-gif-file-formats--monster-character-green-pack-fantasy-illustrations-5386057.png" width="380">
    </div>
    """, unsafe_allow_html=True)

# --- [3. 데이터 로직] ---
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

# --- [4. 메인 UI 화면 구성] ---
score = load_score()
st.markdown(f'<div class="score-badge">🏆 우리 반 점수: {score}점</div>', unsafe_allow_html=True)

st.markdown('<h1 class="super-title">Eco-Bot 챌린지</h1>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # 1단계: 가이드 생성
    if st.session_state.step == 1:
        st.markdown('<span class="card-title">📸 1단계: 배출 전 촬영</span>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">쓰레기통에 넣기 전의 사진을 찍어줘!<br>에코룡이 어떻게 버리는지 감시할 거야.</p>', unsafe_allow_html=True)
        img1 = st.camera_input("촬영하기", key="cam1")
        
        if img1:
            if st.button("에코룡에게 배출법 물어보기 💡"):
                with st.spinner("에코룡이 깐깐하게 분석 중..."):
                    try:
                        prompt = "이 물건의 분리배출법을 한국어로 3줄 요약해줘. 특히 우유팩이라면 반드시 '씻어서 펼치기'를 강조해."
                        res = model.generate_content([prompt, Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    # 2단계: 깐깐한 인증
    elif st.session_state.step == 2:
        st.markdown('<span class="card-title">📝 에코룡의 특명</span>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background:#f0fdf4; padding:25px; border-radius:20px; border:4px solid #059669; margin-bottom:25px; font-size:1.4rem; color:#000000; font-weight:800;">
                {st.session_state.guide}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<span class="card-title">✅ 2단계: 실천 인증샷</span>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">가이드대로 정리했지? <br><b>우유팩이 입체적이면 가차없이 탈락이야!</b></p>', unsafe_allow_html=True)
        img2 = st.camera_input("인증샷 촬영", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("에코룡에게 인증 받기! ✅"):
                    with st.spinner("현미경 검사 중..."):
                        try:
                            verify_prompt = f"""
                            가이드: {st.session_state.guide}
                            너는 세계에서 가장 무서운 환경 감시 공룡 '에코룡'이야.
                            [검사 규칙]
                            1. 우유팩: 반드시 평평하게 펼쳐져 있어야 함. 입체적이면 무조건 '인증실패'.
                            2. 라벨: 페트병 라벨이 남아있으면 '인증실패'.
                            모든 조건이 완벽하면 '인증성공'이라 말하고 칭찬해.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"🚫 반려됨: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 미션 수행하기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- [5. 푸터] ---
st.markdown("<p style='text-align:center; color:#ffffff; font-weight:bold; font-size:1.2rem; margin-top:50px;'>대지고등학교 환경 프로젝트 | 캐릭터: 에코룡 (Eco-Ryong)</p>", unsafe_allow_html=True)
