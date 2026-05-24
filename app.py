import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

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

# --- [2. AI 모델 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

# 모델명 404 에러 방지를 위해 가장 안정적인 이름 사용
model = genai.GenerativeModel('gemini-1.5-flash')

# --- [3. 점수 및 상태 관리 함수] ---
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
        <p style="margin:5px 0 0 0; opacity: 0.9;">가장 똑똑한 분리배출 AI봇</p>
    </div>
    """, unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>우리 반 누적 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# --- [5. 메인 로직] ---

# 1단계: 분석 단계
if st.session_state.step == 1:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🤖</div>
            <div>
                <strong>안녕! 난 에코봇이야.</strong><br>
                쓰레기 사진을 찍으면 어떻게 버리는지 알려줄게!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    img1 = st.camera_input("📸 버리기 전 사진 촬영", key="cam1")
    
    if img1:
        if st.button("AI 분석 시작 💡"):
            with st.spinner("제미나이가 분석 중..."):
                try:
                    # 404 에러 방지를 위해 Image.open으로 열어서 전달
                    res = model.generate_content(["이 쓰레기 분리배출법을 한국어로 딱 3줄 요약해줘. 1.비움 2.제거 3.분류 형식으로!", Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 사용자가 너무 많아요! 10초만 기다렸다가 다시 눌러줘.")
                    else:
                        st.error(f"분석 실패: {e}")

# 2단계: 실천 인증 단계
elif st.session_state.step == 2:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🕵️‍♂️</div>
            <div>
                <strong>정말 가이드대로 했니?</strong><br>
                실천한 모습을 찍어서 나한테 보여줘!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='mission-card'><strong>📝 실천 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    
    img2 = st.camera_input("📸 실천 후 인증샷 촬영", key="cam2")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음부터 다시하기 🔄"): reset_app()

    if img2 and not st.session_state.verified:
        with col2:
            if st.button("최종 인증하기 ✅"):
                with st.spinner("검사 중..."):
                    try:
                        verify_prompt = f"가이드: {st.session_state.guide}. 이 사진이 가이드대로 잘 실천되었는지 확인해줘. 성공했으면 반드시 '인증성공'이라는 단어를 포함해서 칭찬해줘."
                        res = model.generate_content([verify_prompt, Image.open(img2)])
                        
                        if "인증성공" in res.text or "성공" in res.text:
                            add_score()
                            st.session_state.verified = True
                            st.balloons()
                            st.success(res.text)
                        else:
                            st.error(res.text)
                    except Exception as e:
                        st.error(f"인증 실패: {e}")

    if st.session_state.verified:
        if st.button("다음 쓰레기 하러 가기 ➡️"): reset_app()

st.markdown("---")
st.caption("대지고등학교 환경 프로젝트 | Powered by Gemini 1.5 Flash")
