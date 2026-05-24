import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# --- [1. API 설정 및 모델 로드] ---
# Streamlit Cloud의 Settings -> Secrets에 GEMINI_API_KEY를 등록하세요.
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

# 가장 안정적인 Gemini 1.5 Flash 모델 사용 (모델명 절대 안 바뀜)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- [2. 디자인 세팅] ---
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
        background-color: #F0FDF4; padding: 15px; border-radius: 15px;
        border-left: 8px solid #059669; margin: 10px 0; color: #111827;
    }
    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 유틸리티 함수] ---
def get_ai_response(prompt, image):
    """Gemini API 호출 및 에러 처리"""
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ 현재 사용자가 많아 잠시 막혔습니다. 10초 뒤에 다시 시도해주세요!"
        return f"❌ 오류 발생: {e}"

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [4. 앱 상태 관리] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

def reset_app():
    st.session_state.step = 1
    st.session_state.guide = ""
    st.session_state.verified = False
    st.rerun()

# --- [5. UI 화면 구성] ---
st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 26px;">🤖 Eco-Bot 챌린지</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">가장 똑똑하고 안정적인 에코봇</p>
    </div>
    """, unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>현재 우리 반 누적 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# [1단계: 사진 촬영 및 가이드]
if st.session_state.step == 1:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🤖</div>
            <div><strong>반가워! 난 에코봇이야.</strong><br>버릴 쓰레기 사진을 찍어줘.</div>
        </div>
    """, unsafe_allow_html=True)
    
    img1 = st.camera_input("1단계: 사진 찍기", key="cam1")
    
    if img1:
        if st.button("분리배출 가이드 보기 💡"):
            with st.spinner("AI가 분석 중..."):
                prompt = "이 사진 속 물건의 분리배출 방법을 한국어로 3줄 요약해줘. 1.비움, 2.제거, 3.분류 형식으로!"
                res = get_ai_response(prompt, Image.open(img1))
                if "⚠️" in res or "❌" in res:
                    st.warning(res)
                else:
                    st.session_state.guide = res
                    st.session_state.step = 2
                    st.rerun()

# [2단계: 실천 인증]
elif st.session_state.step == 2:
    st.markdown(f"""
        <div class="bot-card">
            <div style="font-size:40px;">🕵️‍♂️</div>
            <div>가이드대로 실천했니? 깨끗해진 사진을 찍어줘!</div>
        </div>
        <div class="mission-card"><strong>📝 실천 미션:</strong><br>{st.session_state.guide}</div>
    """, unsafe_allow_html=True)
    
    img2 = st.camera_input("2단계: 인증 사진 찍기", key="cam2")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음부터 다시하기 🔄"): reset_app()

    if img2 and not st.session_state.verified:
        with col2:
            if st.button("최종 인증 완료 ✅"):
                with st.spinner("검수 중..."):
                    verify_prompt = f"사용자 가이드: {st.session_state.guide}. 사진을 보고 가이드대로 잘 했는지 확인해줘. 성공했다면 무조건 '인증성공'이라는 단어를 포함해서 한 줄로 칭찬해줘."
                    res = get_ai_response(verify_prompt, Image.open(img2))
                    
                    if "인증성공" in res:
                        add_score()
                        st.session_state.verified = True
                        st.balloons()
                        st.success(res)
                    else:
                        st.error(res)

    if st.session_state.verified:
        if st.button("다음 쓰레기 하러 가기 ➡️"): reset_app()

st.markdown("---")
st.caption("대지고등학교 환경 프로젝트 | 모델: Gemini 1.5 Flash (Stable)")
