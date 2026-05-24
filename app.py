import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 브랜딩 & 디자인] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; font-size: 16px; }
    .stApp { background-color: #ECFDF5; } 
    .header-container {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 30px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 20px;
    }
    .bot-card {
        background-color: white; padding: 20px; border-radius: 20px;
        border: 2px solid #A7F3D0; margin-bottom: 15px;
        display: flex; align-items: center; gap: 15px; color: #1F2937;
    }
    .mission-card {
        background-color: white; padding: 15px; border-radius: 15px;
        border-left: 8px solid #059669; margin: 10px 0; color: #111827;
    }
    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 404 에러 원천 차단 모델 로드] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_stable_model():
    # 404 에러를 피하기 위해 사용 가능한 모델 후보군을 순서대로 시도합니다.
    model_candidates = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'models/gemini-1.5-flash']
    
    for model_name in model_candidates:
        try:
            m = genai.GenerativeModel(model_name)
            # 테스트 호출 (아주 짧은 텍스트) 하여 모델이 존재하는지 확인
            m.generate_content("test") 
            return m
        except Exception:
            continue
    
    # 만약 위 후보군이 다 실패하면 시스템에 등록된 모델 중 'flash'가 들어간걸 자동으로 찾습니다.
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                return genai.GenerativeModel(m.name)
    except:
        pass
    return None

model = get_stable_model()

# --- [3. 상태 관리] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

def reset_app():
    st.session_state.step = 1
    st.session_state.guide = ""
    st.session_state.verified = False
    st.rerun()

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [4. 화면 UI 구성] ---
st.markdown('<div class="header-container"><h1>🤖 Eco-Bot 챌린지</h1><p>분리배출 2단계 인증 시스템</p></div>', unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>현재 우리 반 점수: {score}점 🏆</div>", unsafe_allow_html=True)

if not model:
    st.error("❌ 구글 서버에서 모델을 불러올 수 없습니다. API 키가 정상인지, 혹은 잠시 후 다시 시도해주세요.")
    st.stop()

# --- [5. 메인 로직] ---
if st.session_state.step == 1:
    st.markdown('<div class="bot-card"><div><strong>안녕! 에코봇이야.</strong> 쓰레기 사진을 찍으면 버리는 법을 알려줄게!</div></div>', unsafe_allow_html=True)
    img1 = st.camera_input("1단계: 사진 촬영", key="cam1")
    
    if img1:
        if st.button("AI 가이드 받기 💡"):
            with st.spinner("분석 중..."):
                try:
                    res = model.generate_content(["이 쓰레기 분리배출법 3줄 요약해줘. 1.비움 2.제거 3.분류 형식!", Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    if "429" in str(e): st.error("🚨 사용량이 많습니다. 1분만 기다려주세요.")
                    else: st.error(f"오류: {e}")

elif st.session_state.step == 2:
    st.markdown(f"<div class='mission-card'><strong>📝 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    img2 = st.camera_input("2단계: 인증샷 촬영", key="cam2")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 하기 🔄"): reset_app()
    with col2:
        if img2 and not st.session_state.verified:
            if st.button("최종 인증 ✅"):
                with st.spinner("확인 중..."):
                    try:
                        res = model.generate_content([f"가이드: {st.session_state.guide}. 성공했으면 '인증성공'이라 말해줘.", Image.open(img2)])
                        if "인증성공" in res.text or "성공" in res.text:
                            add_score()
                            st.session_state.verified = True
                            st.balloons()
                            st.success(res.text)
                        else: st.error(res.text)
                    except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 쓰레기 하러 가기 ➡️"): reset_app()

st.markdown("---")
st.caption(f"연결된 모델: {model.model_name}")
