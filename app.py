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
        # 모델명을 명확히 지정하여 404 에러 방지
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

# --- [3. 가독성 극대화 및 프리미엄 디자인 CSS] ---
st.set_page_config(page_title="Nature Connect", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');

    /* 배경: 숲 배경 + 전체적으로 어둡게 처리하여 글씨 부각 */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
                    url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* [가독성 핵심] 메인 컨텐츠 카드: 완전한 흰색으로 변경 */
    .service-card {{
        background: #ffffff !important;
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        color: #111827 !important;
        margin: 20px auto;
        max-width: 800px;
        border: 2px solid #e5e7eb;
    }}

    /* 텍스트 스타일: 배경 위 흰색 텍스트는 그림자 추가 */
    .bg-text {{
        color: #ffffff !important;
        text-align: center;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
        font-family: 'Pretendard', sans-serif;
    }}
    
    .main-title {{
        font-size: 5rem !important;
        font-weight: 800;
        margin-bottom: 0px;
    }}

    .sub-title {{
        font-size: 1.3rem;
        letter-spacing: 5px;
        opacity: 0.9;
        margin-bottom: 40px;
    }}

    /* 흰색 막대 등 불필요한 요소 제거 */
    .stDeployButton {{display:none;}}
    iframe {{display:none;}}
    header {{visibility: hidden;}}

    /* 에코룡 위치 조정 */
    .mascot-container {{
        position: fixed;
        bottom: -50px;
        left: -20px;
        width: 350px;
        z-index: 1000;
        pointer-events: none;
    }}
    
    .speech-bubble {{
        position: fixed;
        bottom: 380px;
        left: 40px;
        background: white;
        padding: 20px 25px;
        border-radius: 25px;
        border: 3px solid #059669;
        font-weight: 600;
        color: #064e3b !important;
        z-index: 1001;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        height: 60px !important;
        width: 100% !important;
    }}

    /* [중요] 카메라 입력 창 가독성 */
    .stCameraInput {{
        border: 2px solid #059669 !important;
        border-radius: 20px !important;
        background: white !important;
    }}
    </style>
    
    <div class="speech-bubble">“자연을 위한 오늘의 실천,<br>제가 확인해 드릴게요!”</div>
    <div class="mascot-container">
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

# --- [5. UI 구성] ---

# 상단 텍스트 (배경 위)
st.markdown('<div class="bg-text"><h1 class="main-title">Nature Connect</h1><p class="sub-title">CIRCULAR LIFE PROJECT</p></div>', unsafe_allow_html=True)

col_side, col_main, col_info = st.columns([0.8, 2, 1])

with col_info:
    score = load_score()
    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.9); padding:25px; border-radius:20px; border:2px solid #059669;">
            <p style="margin:0; font-size:0.9rem; color:#666;">CUMULATIVE IMPACT</p>
            <h2 style="margin:5px 0; color:#059669;">{score} Records</h2>
            <p style="font-size:0.85rem; line-height:1.6; color:#333; margin-top:100px;">
                <b>💡 Eco Tip</b><br>
                재활용 마크가 있더라도 이물질이 묻은 용기는 일반 쓰레기로 분류됩니다. 세척이 가장 중요합니다!
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_main:
    st.markdown('<div class="service-card">', unsafe_allow_html=True)
    
    if st.session_state.step == 1:
        st.markdown("### 📸 01. 배출 전 사진 촬영")
        st.write("분류하기 전 물건을 찍어주세요.")
        img1 = st.camera_input("", key="cam1")
        if img1:
            if st.button("AI 분석 시작"):
                with st.spinner("이미지 분석 중..."):
                    try:
                        res = model.generate_content(["이 물건의 분리배출 팁을 2줄 요약해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    elif st.session_state.step == 2:
        st.markdown(f"""
            <div style="background:#f0fdf4; padding:20px; border-radius:15px; border-left:5px solid #059669; margin-bottom:20px;">
                <p style="margin:0; color:#065f46; font-size:1.1rem;"><b>🌱 가이드:</b> {st.session_state.guide}</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("### ✅ 02. 실천 인증")
        st.write("분류가 완료된 상태를 찍어주세요.")
        img2 = st.camera_input("", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 시도"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("인증 완료"):
                    with st.spinner("확인 중..."):
                        try:
                            # 깐깐한 조건 대신 일반적인 분류 성공 여부 확인
                            res = model.generate_content(["사진을 보고 가이드대로 적절히 분류했는지 확인해줘. 성공하면 '인증성공' 단어를 포함해줘.", Image.open(img2)])
                            if "인증성공" in res.text or "성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success("성공적으로 기록되었습니다.")
                            else: st.error(f"결과: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 미션으로 이동"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
