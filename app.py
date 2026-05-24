import streamlit as st
from groq import Groq
from PIL import Image
import base64
import os
import io

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
        border-left: 8px solid #059669; margin: 10px 0; color: #111827;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. Groq AI 자동 모델 선택 (에러 방지)] ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Secrets에 'GROQ_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_vision_model():
    # 현재 Groq에서 쓸 수 있는 비전 모델을 자동으로 찾습니다.
    try:
        models = client.models.list()
        # 1순위: 90b-vision, 2순위: 11b-vision
        available = [m.id for m in models.data if "vision" in m.id]
        if "llama-3.2-90b-vision-preview" in available: return "llama-3.2-90b-vision-preview"
        if "llama-3.2-11b-vision-preview" in available: return "llama-3.2-11b-vision-preview"
        return available[0] # 아무거나 비전 모델 선택
    except:
        return "llama-3.2-90b-vision-preview" # 기본값

WORKING_MODEL = get_vision_model()

# --- [3. 유틸리티 함수] ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def call_ai(prompt, b64_img):
    try:
        res = client.chat.completions.create(
            model=WORKING_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }],
            temperature=0.2,
            max_tokens=500
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"🚨 에러 발생: {e}"

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [4. 메인 화면 구성] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

st.markdown('<div class="header-container"><h1>🤖 Eco-Bot 챌린지</h1><p>분리배출 2단계 인증 시스템</p></div>', unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>현재 우리 반 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# --- [5. 앱 로직] ---
if st.session_state.step == 1:
    st.markdown('<div class="bot-card"><div><strong>안녕! 난 에코봇이야.</strong><br>버릴 물건 사진을 찍으면 버리는 법을 알려줄게!</div></div>', unsafe_allow_html=True)
    img1 = st.camera_input("1단계: 버리기 전 사진")
    if img1:
        if st.button("AI 가이드 받기 💡"):
            with st.spinner("AI 분석 중..."):
                b64 = encode_image(img1)
                res = call_ai("이 물건의 분리배출 방법을 한국어로 딱 3줄 요약해줘. 1.비움 2.제거 3.분류 형식!", b64)
                st.session_state.guide = res
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    st.markdown(f"<div class='mission-card'><strong>📝 배출 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    img2 = st.camera_input("2단계: 실천 후 인증")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음으로 🔄"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if img2 and not st.session_state.verified:
            if st.button("인증하기 ✅"):
                with st.spinner("검사 중..."):
                    b64_2 = encode_image(img2)
                    v_prompt = f"가이드: {st.session_state.guide}. 사진을 보고 가이드대로 잘 했는지 확인해줘. 성공했으면 '인증성공'이라 말해줘."
                    res = call_ai(v_prompt, b64_2)
                    if "인증성공" in res or "성공" in res:
                        add_score()
                        st.session_state.verified = True
                        st.balloons()
                        st.success(res)
                    else:
                        st.error(res)

    if st.session_state.verified:
        if st.button("다음 쓰레기 하기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

st.markdown("---")
st.caption(f"안정적인 Groq Llama Vision 엔진 가동 중 | 모델: {WORKING_MODEL}")
