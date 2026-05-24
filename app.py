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

# --- [2. Groq AI 클라이언트 설정] ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Secrets에 'GROQ_API_KEY'를 등록해주세요!")
    st.stop()

# --- [3. 에러 해결 핵심: 살아있는 비전 모델 자동 찾기] ---
@st.cache_resource
def find_live_vision_model():
    try:
        # 현재 Groq 서버에서 사용 가능한 모든 모델 리스트를 가져옵니다.
        models = client.models.list().data
        # 이름에 'vision'이 들어간 모델들만 추출합니다.
        vision_models = [m.id for m in models if "vision" in m.id.lower()]
        
        # 우선순위대로 골라봅니다.
        # 1. 90b(고성능) -> 2. 11b(보통) -> 3. llava(기본)
        for pref in ["llama-3.2-90b-vision", "llama-3.2-11b-vision", "llava"]:
            for m in vision_models:
                if pref in m:
                    return m
        # 없으면 비전 모델 중 첫 번째꺼 반환
        return vision_models[0] if vision_models else "llama-3.2-11b-vision-preview"
    except Exception:
        # 리스트 조회 실패 시 가장 확률 높은 모델명 수동 반환
        return "llama-3.2-11b-vision-preview"

WORKING_MODEL = find_live_vision_model()

# --- [4. 유틸리티 함수] ---
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
            temperature=0.1
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"🚨 분석 중 오류 발생: {e}"

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [5. 앱 UI 로직] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

st.markdown('<div class="header-container"><h1>🤖 Eco-Bot 챌린지</h1><p>살아있는 AI 엔진 자동 연결 중</p></div>', unsafe_allow_html=True)

score = load_score()
st.info(f"🏆 현재 우리 반 누적 점수: {score}점")

if st.session_state.step == 1:
    st.markdown('<div class="bot-card"><div><strong>안녕! 에코봇이야.</strong><br>버릴 물건 사진을 찍으면 방법을 알려줄게!</div></div>', unsafe_allow_html=True)
    img1 = st.camera_input("1단계: 버리기 전 사진")
    if img1:
        if st.button("AI 분석 시작 💡"):
            with st.spinner("최적의 모델로 분석 중..."):
                b64 = encode_image(img1)
                res = call_ai("이 물건의 분리배출 방법 3줄 요약. 1.비움 2.제거 3.분류 형식으로 한국어로!", b64)
                st.session_state.guide = res
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    st.markdown(f"<div class='mission-card'><strong>📝 배출 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    img2 = st.camera_input("2단계: 실천 후 인증")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 하기 🔄"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if img2 and not st.session_state.verified:
            if st.button("최종 인증 ✅"):
                with st.spinner("검수 중..."):
                    b64_2 = encode_image(img2)
                    res = call_ai(f"가이드: {st.session_state.guide}. 사진을 보고 잘 했으면 '인증성공'이라 말해줘.", b64_2)
                    if "인증성공" in res or "성공" in res:
                        add_score()
                        st.session_state.verified = True
                        st.balloons()
                        st.success(res)
                    else: st.error(res)

    if st.session_state.verified:
        if st.button("다음 쓰레기 인증하기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

st.markdown("---")
st.caption(f"연결된 엔진: {WORKING_MODEL} (자동 업데이트 완료)")
