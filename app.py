import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. API 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# --- [2. 역대급 가독성 디자인 (검정 글씨 + 흰색 테두리)] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🦖", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@900&display=swap');

    /* 배경: 숲 배경 고정 */
    .stApp {
        background: url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 흰색 박스 제거 및 모든 텍스트 외곽선 설정 (검정 글씨 + 흰색 테두리) */
    h1, h2, h3, h4, p, span, label, .stMarkdown {
        color: #000000 !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 900 !important;
        /* 흰색 외곽선 효과 (text-shadow 8방향) */
        text-shadow: 
            -3px -3px 0 #fff,  
             3px -3px 0 #fff,
            -3px  3px 0 #fff,
             3px  3px 0 #fff,
             0px -3px 0 #fff,
             0px  3px 0 #fff,
            -3px  0px 0 #fff,
             3px  0px 0 #fff;
    }

    /* 메인 타이틀: 더 크고 확실하게 */
    .main-title {
        font-family: 'Black Han Sans', sans-serif !important;
        font-size: 5.5rem !important;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* 캐릭터 에코룡 (좌측 하단 고정 일러스트) */
    .mascot-container {
        position: fixed;
        bottom: 0px;
        left: 20px;
        width: 380px;
        z-index: 999;
    }
    
    .speech-bubble {
        position: fixed;
        bottom: 350px;
        left: 60px;
        background: #fde047;
        color: black !important;
        padding: 20px 30px;
        border-radius: 30px;
        border: 4px solid black;
        font-weight: 900 !important;
        font-size: 1.5rem;
        z-index: 1000;
        box-shadow: 8px 8px 0px rgba(0,0,0,0.3);
        text-shadow: none !important; /* 말풍선 안은 테두리 제거 */
    }

    /* 점수판 디자인 */
    .score-badge {
        position: fixed;
        top: 30px;
        right: 40px;
        background: #fde047;
        color: black !important;
        padding: 20px 40px;
        border: 5px solid black;
        border-radius: 20px;
        font-family: 'Black Han Sans', sans-serif !important;
        font-size: 2.2rem;
        z-index: 1000;
        text-shadow: none !important;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background: #059669 !important;
        color: white !important;
        border: 5px solid white !important;
        border-radius: 20px !important;
        font-size: 1.8rem !important;
        font-weight: 900 !important;
        height: 80px !important;
        width: 100% !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
        text-shadow: none !important;
    }
    
    /* 카메라 입력창 테두리 */
    .stCameraInput {
        border: 5px solid white !important;
        border-radius: 20px !important;
    }
    </style>
    
    <!-- 오리지널 캐릭터 에코룡과 말풍선 -->
    <div class="speech-bubble">거기 너! <br>우유팩 안 펼치면 <br>에코룡이 혼내준다! 🦖</div>
    <div class="mascot-container">
        <img src="https://cdni.iconscout.com/illustration/premium/thumb/cute-dinosaur-illustration-download-in-svg-png-gif-file-formats--monster-character-green-pack-fantasy-illustrations-5386057.png" width="380">
    </div>
    """, unsafe_allow_html=True)

# --- [3. 데이터 및 상태 관리] ---
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
st.markdown(f'<div class="score-badge">🏆 {score}점</div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Eco-Bot 챌린지</h1>', unsafe_allow_html=True)

# 중앙 정렬을 위한 컬럼 구성
col_left, col_main, col_right = st.columns([1, 4, 1])

with col_main:
    # 1단계: 분석
    if st.session_state.step == 1:
        st.markdown("### 📸 1단계: 배출 전 촬영")
        st.markdown("<p>쓰레기통에 넣기 전 사진을 찍으세요. 에코룡이 감시합니다!</p>", unsafe_allow_html=True)
        img1 = st.camera_input("", key="cam1")
        if img1:
            if st.button("에코룡에게 검사받기 💡"):
                with st.spinner("에코룡이 분석 중..."):
                    try:
                        res = model.generate_content(["이 물건의 분리배출법 3줄 요약. 우유팩은 반드시 펼치라고 강조해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    # 2단계: 인증
    elif st.session_state.step == 2:
        st.markdown("### 📝 에코룡의 지시사항")
        st.markdown(f"<p>{st.session_state.guide}</p>", unsafe_allow_html=True)
        
        st.markdown("### ✅ 2단계: 실천 인증샷")
        st.markdown("<p>가이드대로 정리했나요? 우유팩이 펼쳐져 있지 않으면 탈락입니다!</p>", unsafe_allow_html=True)
        img2 = st.camera_input("", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("인증 완료 ✅"):
                    with st.spinner("현미경 검토 중..."):
                        try:
                            verify_prompt = f"가이드: {st.session_state.guide}. 사진을 보고 우유팩이 평평하게 펼쳐져 있는지 검사해. 완벽하면 '인증성공'이라 말해줘."
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"판정 결과: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 미션 하러 가기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

st.markdown("<p style='text-align:center; margin-top:50px;'>대지고등학교 환경 프로젝트 | 캐릭터: 에코룡</p>", unsafe_allow_html=True)
