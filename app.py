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
    .stApp { background-color: #ECFDF5; } /* 연한 초록 배경 */
    
    .header-container {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 30px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .bot-card {
        background-color: white; padding: 20px; border-radius: 20px;
        border: 2px solid #A7F3D0; margin-bottom: 15px;
        display: flex; align-items: center; gap: 15px;
    }
    
    .mission-card {
        background-color: white; padding: 15px; border-radius: 15px;
        border-left: 8px solid #059669; margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. AI 모델 자동 타겟팅 (404 에러 해결사)] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_best_model():
    try:
        # 내 키로 사용 가능한 모델 리스트를 싹 다 가져옵니다.
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 1순위: flash, 2순위: pro, 3순위: 아무거나 첫번째
        if "models/gemini-1.5-flash" in models: return genai.GenerativeModel("gemini-1.5-flash")
        elif "models/gemini-1.5-flash-latest" in models: return genai.GenerativeModel("gemini-1.5-flash-latest")
        elif "models/gemini-1.5-pro" in models: return genai.GenerativeModel("gemini-1.5-pro")
        else: return genai.GenerativeModel(models[0].replace("models/", ""))
    except Exception as e:
        st.error(f"모델 찾기 실패: {e}")
        return None

model = get_best_model()

# --- [3. 상태 관리 및 데이터] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

def reset_app():
    for key in ['step', 'guide', 'verified']:
        if key in st.session_state: del st.session_state[key]
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

st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 26px;">🤖 Eco-Bot 챌린지</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">분리배출 2단계 인증 시스템</p>
    </div>
    """, unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>현재 우리 반 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# --- [5. 메인 2단계 로직] ---

if st.session_state.step == 1:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🤖</div>
            <div>
                <strong>안녕! 난 에코봇이야.</strong><br>
                쓰레기 사진을 찍으면 짧고 굵게 방법을 알려줄게!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    img1 = st.camera_input("1단계: 버리기 전 사진 촬영", key="cam1")
    
    if img1:
        if st.button("AI 가이드 받기 💡"):
            with st.spinner("분석 중..."):
                try:
                    res = model.generate_content(["이 쓰레기 분리배출법을 딱 3줄로 요약해줘. 1.비움 2.제거 3.분류 형식으로!", Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e: st.error(f"분석 실패: {e}")

elif st.session_state.step == 2:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🕵️‍♂️</div>
            <div>
                <strong>실천하고 다시 찍어줘!</strong><br>
                제대로 했는지 내가 검사해볼게.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='mission-card'><strong>📝 배출 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    
    img2 = st.camera_input("2단계: 실천 후 사진 촬영", key="cam2")
    
    if st.button("처음부터 다시하기 🔄"): reset_app()

    if img2 and not st.session_state.verified:
        if st.button("최종 인증하기 ✅"):
            with st.spinner("검사 중..."):
                try:
                    verify_prompt = f"사용자 가이드: {st.session_state.guide}. 사진을 보고 미션을 잘 했는지 확인해줘. 성공하면 무조건 '인증성공'이라는 단어를 포함해서 한 줄로 칭찬해줘. 아니면 부족한 점을 딱 한 줄만 말해줘."
                    res = model.generate_content([verify_prompt, Image.open(img2)])
                    
                    if "인증성공" in res.text or "성공" in res.text:
                        add_score()
                        st.session_state.verified = True
                        st.balloons()
                        st.success(res.text)
                    else:
                        st.error(res.text)
                except Exception as e: st.error(f"검사 실패: {e}")

    if st.session_state.verified:
        if st.button("다음 쓰레기 하러 가기 ➡️"): reset_app()

st.markdown("---")
st.caption("대지고등학교 환경 프로젝트 | Made by Vibe Coding")
