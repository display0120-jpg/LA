import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 브랜딩 & 디자인 세팅] ---
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bot-card {
        background-color: white; padding: 20px; border-radius: 20px;
        border: 2px solid #A7F3D0; margin-bottom: 15px;
        display: flex; align-items: center; gap: 15px; color: #1F2937;
    }
    .mission-card {
        background-color: white; padding: 15px; border-radius: 15px;
        border-left: 8px solid #059669; margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #111827;
    }
    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. AI 모델 자동 선택 로직 (404 해결사)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def load_best_model():
    try:
        # 현재 내 API 키로 사용 가능한 모델 리스트를 싹 다 긁어옵니다.
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1순위: gemini-1.5-flash, 2순위: gemini-pro-vision, 3순위: 아무거나 첫번째
        target = ""
        if any("gemini-1.5-flash" in m for m in models):
            target = "gemini-1.5-flash"
        elif any("gemini-pro-vision" in m for m in models):
            target = "gemini-pro-vision"
        else:
            target = models[0].replace("models/", "")
            
        return genai.GenerativeModel(target)
    except Exception as e:
        st.error(f"모델 로드 실패: {e}")
        return None

model = load_best_model()

# --- [3. 점수 및 상태 관리] ---
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

# --- [4. UI 화면 구성] ---
st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 26px;">🤖 Eco-Bot 챌린지</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">실시간 AI 분리배출 도우미</p>
    </div>
    """, unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>우리 반 누적 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# --- [5. 메인 로직] ---
if st.session_state.step == 1:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🤖</div>
            <div><strong>안녕! 에코봇이야.</strong><br>쓰레기 사진을 찍으면 버리는 법을 알려줄게!</div>
        </div>
    """, unsafe_allow_html=True)
    
    img1 = st.camera_input("1단계: 사진 촬영")
    if img1:
        if st.button("AI 분석 시작 💡"):
            with st.spinner("AI 분석 중..."):
                try:
                    res = model.generate_content(["이 쓰레기 분리배출법을 한국어로 3줄 요약해줘. 1.비움 2.제거 3.분류 형식!", Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 중 오류: {e}")

elif st.session_state.step == 2:
    st.markdown(f"<div class='mission-card'><strong>📝 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    img2 = st.camera_input("2단계: 인증샷 촬영")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 하기 🔄"): reset_app()
    with col2:
        if img2 and st.button("인증 완료 ✅"):
            with st.spinner("확인 중..."):
                try:
                    res = model.generate_content([f"가이드: {st.session_state.guide}. 사진을 보고 성공했으면 '인증성공'이라 말해줘.", Image.open(img2)])
                    if "인증성공" in res.text or "성공" in res.text:
                        add_score()
                        st.session_state.verified = True
                        st.balloons()
                        st.success(res.text)
                    else: st.error(res.text)
                except Exception as e:
                    st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 쓰레기 하기 ➡️"): reset_app()

st.markdown("---")
st.caption(f"현재 사용 중인 AI 모델: {model.model_name if model else '연결 안됨'}")
