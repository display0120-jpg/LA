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

# --- [2. 고대비 디자인 & 캐릭터 일러스트 CSS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@700;900&display=swap');

    /* 배경: 숲 배경을 유지하되 중앙부 가독성을 위해 밝은 광원 효과 추가 */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.2)), 
                    url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 메인 카드: 가독성을 위해 불투명한 흰색 배경과 진한 테두리 */
    .main-container {
        background: #ffffff;
        border-radius: 40px;
        padding: 50px;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3);
        margin: 50px auto;
        max-width: 850px;
        border: 10px solid #059669; /* 진한 초록 테두리 */
        position: relative;
        z-index: 1;
    }

    /* 캐릭터 에코룡 (2D 일러스트 스타일 고정) */
    .mascot-container {
        position: fixed;
        bottom: 30px;
        left: 50px;
        width: 320px;
        z-index: 100;
        filter: drop-shadow(5px 5px 15px rgba(0,0,0,0.2));
    }
    
    .speech-bubble {
        position: fixed;
        bottom: 380px;
        left: 80px;
        background: #059669;
        color: white;
        padding: 20px 30px;
        border-radius: 30px;
        border-bottom-left-radius: 2px;
        font-family: 'Pretendard', sans-serif;
        font-weight: 800;
        font-size: 1.2rem;
        z-index: 101;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
    }

    /* 가독성 1순위: 제목 디자인 */
    .super-title {
        font-family: 'Black Han Sans', sans-serif;
        font-size: 4.5rem;
        color: #065f46;
        text-align: center;
        text-shadow: 3px 3px 0px #ffffff;
        margin-top: 40px;
        letter-spacing: -2px;
    }

    /* 카드 내 텍스트: 매우 진하게 설정 */
    .card-title {
        color: #064e3b;
        font-family: 'Pretendard', sans-serif;
        font-weight: 900;
        font-size: 2.2rem;
        margin-bottom: 20px;
        display: block;
        border-bottom: 6px solid #10b981;
        width: fit-content;
    }

    .info-text {
        color: #111827; /* 거의 검은색에 가까운 진한 회색 */
        font-size: 1.3rem;
        line-height: 1.6;
        font-weight: 700;
    }

    /* 버튼 스타일: 눈에 확 띄게 */
    .stButton>button {
        background: #059669 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 15px 30px !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        width: 100% !important;
        box-shadow: 0 8px 0px #047857 !important;
        transition: all 0.1s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 0px #047857 !important;
    }

    /* 점수판 */
    .score-badge {
        position: fixed;
        top: 40px;
        right: 50px;
        background: #fde047;
        color: #000;
        padding: 20px 40px;
        border: 5px solid #000;
        border-radius: 50px;
        font-family: 'Black Han Sans', sans-serif;
        font-size: 1.8rem;
        z-index: 100;
    }
    </style>
    
    <!-- 캐릭터: 에코룡 (2D 공룡 캐릭터 일러스트) -->
    <div class="speech-bubble">우유팩 안 펼치면<br>내가 다 먹어버린다! 🦖</div>
    <div class="mascot-container">
        <img src="https://cdni.iconscout.com/illustration/premium/thumb/cute-dinosaur-illustration-download-in-svg-png-gif-file-formats--monster-character-green-pack-fantasy-illustrations-5386057.png" width="300">
    </div>
    """, unsafe_allow_html=True)

# --- [3. 점수 관리] ---
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

# --- [4. 메인 화면 구성] ---
score = load_score()
st.markdown(f'<div class="score-badge">🏆 현재 점수: {score}점</div>', unsafe_allow_html=True)

st.markdown('<h1 class="super-title">Eco-Bot 챌린지</h1>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # 1단계
    if st.session_state.step == 1:
        st.markdown('<span class="card-title">📸 1단계: 원래 상태 촬영</span>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">에코룡에게 쓰레기를 보여주세요. <br>어떻게 버려야 할지 분석해 드릴게요!</p>', unsafe_allow_html=True)
        img1 = st.camera_input("카메라 실행", key="cam1")
        
        if img1:
            if st.button("에코룡아, 배출법 알려줘! 💡"):
                with st.spinner("에코룡이 분석 중..."):
                    try:
                        res = model.generate_content(["이 물건의 분리배출법을 한국어로 3줄 요약해줘. 특히 우유팩이라면 반드시 '씻어서 펼치기'를 강조해.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    # 2단계
    elif st.session_state.step == 2:
        st.markdown('<span class="card-title">📝 에코룡의 지시사항</span>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background:#f0fdf4; padding:25px; border-radius:20px; border:3px solid #059669; margin-bottom:25px; font-size:1.3rem; color:#064e3b; font-weight:700;">
                {st.session_state.guide}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<span class="card-title">✅ 2단계: 실천 인증샷</span>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">가이드대로 처리했나요? <br><b>우유팩 펼치기</b> 등이 안 되어 있으면 탈락입니다!</p>', unsafe_allow_html=True)
        img2 = st.camera_input("인증 사진 촬영", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("인증 요청하기 ✅"):
                    with st.spinner("에코룡이 눈 크게 뜨고 검사 중..."):
                        try:
                            verify_prompt = f"""
                            가이드: {st.session_state.guide}
                            너는 깐깐한 공룡 감독관이야. 사진을 보고 기준을 하나라도 어기면 무조건 '인증실패'라고 말해.
                            [기준]
                            1. 우유팩: 반드시 펼쳐져서 평평해야 함. 입체적이면 무조건 탈락.
                            2. 페트병: 라벨이 제거되어야 함.
                            완벽하면 '인증성공'이라 말해줘.
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
        if st.button("다음 물건 하러 가기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- [5. 하단 정보] ---
st.markdown("<p style='text-align:center; color:#065f46; font-weight:bold; font-size:1.2rem; margin-top:50px;'>대지고등학교 환경 프로젝트 | 에코룡은 당신의 양심을 지켜봅니다.</p>", unsafe_allow_html=True)
