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

# --- [2. AI 모델 설정 (1.5 Flash 강제 고정)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

# 하루 1,500회 가능한 안정 모델로 '강제 지정'
# 실험용 2.5 모델(하루 20회 제한)을 절대 쓰지 않게 합니다.
MODEL_NAME = 'gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

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
st.markdown('<div class="header-container"><h1>🤖 Eco-Bot 챌린지</h1><p>안정적인 1.5 엔진 가동 중</p></div>', unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>현재 우리 반 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# --- [5. 메인 로직] ---
if st.session_state.step == 1:
    st.markdown('<div class="bot-card"><div><strong>안녕! 에코봇이야.</strong><br>쓰레기 사진을 찍으면 버리는 법을 알려줄게!</div></div>', unsafe_allow_html=True)
    img1 = st.camera_input("1단계: 사진 촬영", key="cam1")
    
    if img1:
        if st.button("AI 가이드 받기 💡"):
            with st.spinner("AI 분석 중..."):
                try:
                    res = model.generate_content(["이 쓰레기 분리배출법 3줄 요약해줘. 1.비움 2.제거 3.분류 형식!", Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 오늘 사용량을 모두 소모했습니다. (하루 20회 제한 모델에 걸렸을 수 있습니다.) 모델 설정을 다시 확인하세요.")
                    else:
                        st.error(f"오류: {e}")

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
                    except Exception as e:
                        st.error(f"인증 오류: {e}")

    if st.session_state.verified:
        if st.button("다음 쓰레기 하러 가기 ➡️"): reset_app()
