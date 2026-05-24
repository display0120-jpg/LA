import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. API 및 AI 모델 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_stable_model():
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = get_stable_model()

# --- [2. 이미지 로드 로직] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 디자인 커스텀 (흰색 막대 제거 및 가독성 끝판왕)] ---
st.set_page_config(page_title="Nature Connect", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');

    /* [필살기] 상단 흰색 막대 및 불필요한 Streamlit 요소 완전 제거 */
    header {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    footer {{visibility: hidden !important;}}
    .block-container {{padding-top: 2rem !important;}}

    /* 전체 배경: 어두운 숲 배경으로 글씨 대비 극대화 */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                    url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* 메인 카드: 완전 불투명 화이트 (가독성 100%) */
    .content-card {{
        background: #ffffff !important;
        border-radius: 30px;
        padding: 50px;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        color: #111827 !important;
        margin: 0 auto;
        max-width: 850px;
        border: 4px solid #059669;
    }}

    /* 상단 타이틀 디자인 */
    .title-area {{
        text-align: center;
        color: #ffffff !important;
        text-shadow: 0px 4px 15px rgba(0,0,0,1);
        margin-bottom: 50px;
    }}
    .main-title {{ font-size: 5.5rem !important; font-weight: 800; margin: 0; }}
    .sub-title {{ font-size: 1.4rem; letter-spacing: 6px; opacity: 0.8; font-weight: 300; }}

    /* 에코룡 & 말풍선 */
    .mascot-box {{
        position: fixed;
        bottom: -50px;
        left: -30px;
        width: 380px;
        z-index: 1000;
        pointer-events: none;
    }}
    .speech-bubble {{
        position: fixed;
        bottom: 420px;
        left: 50px;
        background: #059669;
        color: white !important;
        padding: 20px 30px;
        border-radius: 25px;
        border-bottom-left-radius: 2px;
        font-weight: 600;
        z-index: 1001;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        height: 70px !important;
        width: 100% !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{ background: #065f46 !important; transform: translateY(-3px); }}

    /* 텍스트 가독성 강제 고정 */
    h3, p, label {{ color: #111827 !important; font-weight: 700 !important; }}
    </style>
    
    <div class="speech-bubble">지구를 위한 당신의 발걸음,<br>제가 끝까지 함께할게요! 🦖</div>
    <div class="mascot-box">
        <img src="{mascot_src}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [4. 데이터 로직] ---
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

# --- [5. 메인 UI 화면 구성] ---

# 타이틀
st.markdown('<div class="title-area"><h1 class="main-title">Nature Connect</h1><p class="sub-title">CIRCULAR LIFE PROJECT</p></div>', unsafe_allow_html=True)

col_empty, col_main, col_stat = st.columns([0.2, 2.5, 1])

# 오른쪽 통계 (세련되게 꾸밈)
with col_stat:
    score = load_score()
    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.95); padding:30px; border-radius:25px; border-top:8px solid #059669; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <p style="margin:0; font-size:0.9rem; color:#666; font-weight:800;">TOTAL ACTIONS</p>
            <h1 style="margin:10px 0; color:#059669; font-size:3.5rem;">{score}</h1>
            <p style="color:#111827; font-size:1rem; border-top:1px solid #eee; padding-top:20px;">
                <b>오늘의 환경 메시지</b><br>
                당신의 한 번의 분류가 죽어가는 숲을 살리는 강력한 힘이 됩니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

# 중앙 메인 컨텐츠
with col_main:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    
    if st.session_state.step == 1:
        st.markdown("### 🔍 01. 대상 탐색")
        st.write("순환이 필요한 물건을 카메라에 담아주세요. AI가 최선의 방법을 제안합니다.")
        img1 = st.camera_input("Scanner", key="cam1")
        if img1:
            if st.button("분석 엔진 가동"):
                with st.spinner("자원을 식별하고 있습니다..."):
                    try:
                        res = model.generate_content(["이 물건의 분리배출 팁을 간결하게 2줄로 설명해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    elif st.session_state.step == 2:
        st.markdown(f"""
            <div style="background:#f0fdf4; padding:25px; border-radius:20px; border-left:8px solid #059669; margin-bottom:30px;">
                <p style="margin:0; color:#065f46; font-size:1.2rem;"><b>🌱 가이드:</b> {st.session_state.guide}</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("### ✨ 02. 가치 증명")
        st.write("완성된 선순환의 모습을 렌즈로 기록하여 증명해주세요.")
        img2 = st.camera_input("Proof", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("처음으로"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("실천 기록하기"):
                    with st.spinner("실천 내용을 검증하는 중입니다..."):
                        try:
                            res = model.generate_content(["가이드대로 적절히 분류되었는지 확인해줘. 성공하면 반드시 '인증성공' 단어를 포함해줘.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("소중한 변화가 기록되었습니다.")
                            else: st.error(f"결과: {res.text}")
                        except Exception as e: st.error(f"Error: {e}")

    if st.session_state.verified:
        if st.button("새로운 순환 시작하기"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
