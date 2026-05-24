import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. 기본 설정 및 AI 연결] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🌱", layout="wide")

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

# --- [2. 고품격 서비스 디자인 (CSS)] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');

    /* 전체 배경: 화면을 꽉 채우는 고화질 자연 배경 + 어두운 오버레이 */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                    url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Pretendard', sans-serif;
    }

    /* 메인 컨테이너: 가독성을 위한 화이트 보드 스타일 */
    .service-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 40px;
        padding: 50px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin: 20px auto;
        max-width: 900px;
        min-height: 70vh;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* 마스코트 에코루 (2D 일러스트 느낌) 고정 배치 */
    .mascot-img {
        position: fixed;
        bottom: 20px;
        right: 40px;
        width: 280px;
        z-index: 100;
        filter: drop-shadow(0 10px 15px rgba(0,0,0,0.3));
    }

    /* 캐릭터 말풍선 */
    .speech-bubble {
        position: fixed;
        bottom: 320px;
        right: 60px;
        background: #065f46;
        color: white;
        padding: 20px 25px;
        border-radius: 30px;
        border-bottom-right-radius: 5px;
        width: 240px;
        font-weight: 700;
        z-index: 101;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }

    /* 타이틀 및 텍스트 */
    .title-text {
        color: #064e3b;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    .sub-title {
        text-align: center;
        color: #059669;
        font-size: 1.3rem;
        margin-bottom: 40px;
    }

    /* 버튼 스타일 (프리미엄 느낌) */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 20px 40px !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(16, 185, 129, 0.4) !important;
    }

    /* 단계별 배지 */
    .step-badge {
        background: #dcfce7;
        color: #166534;
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 15px;
    }
    </style>

    <!-- 마스코트 에코루 이미지 (2D 스타일) -->
    <div class="speech-bubble">안녕! 나 에코루야. <br>너의 분리배출을 도와줄게. <br>제대로 안하면 알지? 🤨</div>
    <img src="https://cdni.iconscout.com/illustration/premium/thumb/robot-keeping-environment-clean-4488344-3738435.png" class="mascot-img">
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

# --- [4. 메인 화면 레이아웃] ---
st.markdown('<div class="service-container">', unsafe_allow_html=True)

st.markdown('<h1 class="title-text">Eco-Bot Challenge</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">지구를 지키는 가장 스마트한 2단계 분리배출 시스템</p>', unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:right; font-weight:700; color:#065f46; margin-bottom:20px;'>🏆 누적 점수: {score}점</div>", unsafe_allow_html=True)

# --- 1단계: 미션 시작 ---
if st.session_state.step == 1:
    st.markdown('<span class="step-badge">STEP 01</span>', unsafe_allow_html=True)
    st.markdown("### 📸 버리기 전의 상태를 찍어주세요")
    st.write("에코루가 사진을 보고 어떻게 분리해야 하는지 분석해 드릴게요.")
    
    img1 = st.camera_input("촬영하기", key="cam1")
    
    if img1:
        if st.button("분리배출 미션 받기 💡"):
            with st.spinner("에코루가 분석 중..."):
                try:
                    prompt = "이 물건의 분리배출 방법을 알려줘. 특히 펼치기, 씻기, 라벨 떼기 등 '행동' 위주로 한국어로 3줄 요약해줘."
                    res = model.generate_content([prompt, Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e: st.error(f"오류: {e}")

# --- 2단계: 초정밀 인증 ---
elif st.session_state.step == 2:
    st.markdown('<span class="step-badge">STEP 02</span>', unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background:#f8fafc; padding:25px; border-radius:20px; border:2px dashed #cbd5e1; margin-bottom:30px;">
            <h4 style="margin:0 0 10px 0; color:#1e293b;">📋 실천 미션</h4>
            <p style="font-size:1.1rem; line-height:1.6; color:#475569;">{st.session_state.guide}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✅ 실천 완료 인증샷")
    st.write("우유팩 펼치기, 페트병 라벨 제거 등이 안 되어 있으면 반려됩니다.")
    
    img2 = st.camera_input("인증하기", key="cam2")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("다시 시작 🔄"):
            st.session_state.step = 1; st.rerun()
    with c2:
        if img2 and not st.session_state.verified:
            if st.button("에코루에게 최종 검토받기 ✅"):
                with st.spinner("현미경 검사 중..."):
                    try:
                        # 깐깐한 검수 프롬프트
                        verify_prompt = f"""
                        가이드: {st.session_state.guide}
                        사진을 보고 미션을 완벽히 수행했는지 검사해.
                        1. 우유팩/상자: 반드시 평평하게 펼쳐져 있어야 함. 입체적이면 절대 안 됨.
                        2. 플라스틱: 라벨이 제거되어야 함.
                        모든 기준에 부합하면 '인증성공'이라 말하고, 하나라도 부족하면 '인증실패'와 함께 이유를 말해.
                        """
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
        if st.button("다음 미션으로 이동 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- [5. 푸터 정보] ---
st.markdown("""
    <div style="text-align:center; color:white; padding:20px; font-weight:700;">
        © 2024 대지고등학교 환경 프로젝트 팀 | Powered by Gemini AI
    </div>
    """, unsafe_allow_html=True)
