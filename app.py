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
        # 현재 사용 가능한 모델 리스트를 조회하여 1.5-flash 자동 연결
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(target)
    except: return None

model = get_stable_model()

# --- [2. 이미지 로드 로직] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

ecoryong_b64 = get_base64_image("ecoryong.png")
mascot_src = f"data:image/png;base64,{ecoryong_b64}" if ecoryong_b64 else ""

# --- [3. 세련된 프리미엄 디자인 CSS] ---
st.set_page_config(page_title="Nature Connect", page_icon="🌿", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Pretendard:wght@300;600;800&display=swap');

    /* 배경: 고화질 숲 + 부드러운 다크 레이어 */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)),
                    url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* 글래스모피즘 메인 컨테이너 */
    .glass-card {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-radius: 30px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        color: #1a2e1a;
    }}

    /* 텍스트 스타일: 가독성 중심 */
    h1, h2, h3, p, span, label {{
        font-family: 'Gowun Batang', serif !important;
        color: #1a2e1a !important;
    }}
    
    .main-title {{
        font-size: 4.5rem !important;
        font-weight: 700;
        text-align: center;
        color: #ffffff !important;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.4);
        margin-bottom: 5px;
    }}

    .sub-title {{
        font-family: 'Pretendard', sans-serif !important;
        font-size: 1.2rem;
        text-align: center;
        color: rgba(255,255,255,0.9) !important;
        margin-bottom: 50px;
        letter-spacing: 3px;
    }}

    /* 우측 통계 패널 */
    .stat-panel {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white !important;
    }}

    /* 에코룡 캐릭터 & 말풍선 (좌측 하단) */
    .mascot-container {{
        position: fixed;
        bottom: -50px;
        left: -30px;
        width: 380px;
        z-index: 999;
        pointer-events: none;
    }}
    
    .speech-bubble {{
        position: fixed;
        bottom: 450px;
        left: 30px;
        background: rgba(255, 255, 255, 0.95);
        padding: 20px 30px;
        border-radius: 25px;
        border-bottom-left-radius: 2px;
        font-weight: 600;
        color: #064e3b !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background: #2d5a27 !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background: #3e7a36 !important;
        transform: translateY(-2px);
    }}
    </style>
    
    <div class="speech-bubble">“오늘도 자연을 위한<br>작은 기록을 시작해볼까요?”</div>
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

# --- [5. 메인 UI 레이아웃] ---
st.markdown('<h1 class="main-title">Nature Connect</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">CIRCULAR LIFE PROJECT</p>', unsafe_allow_html=True)

col_left, col_main, col_right = st.columns([1, 2.5, 1.2])

# [오른쪽: 세련된 통계 패널]
with col_right:
    score = load_score()
    st.markdown(f"""
        <div class="stat-panel">
            <p style="margin:0; font-size:0.9rem; opacity:0.8;">OUR IMPACT</p>
            <h2 style="margin:10px 0; color:white !important;">현재 {score}번의 실천</h2>
            <hr style="opacity:0.2;">
            <p style="font-size:0.85rem; line-height:1.6; opacity:0.9;">
                <b>💡 오늘의 에코 팁</b><br>
                영수증은 재활용이 되지 않는 일반 쓰레기입니다. 모바일 영수증을 애용해 주세요!
            </p>
        </div>
    """, unsafe_allow_html=True)

# [중앙: 메인 액션 카드]
with col_main:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if not model:
        st.error("AI 엔진을 불러올 수 없습니다. API 키를 확인해주세요.")
    else:
        if st.session_state.step == 1:
            st.markdown("### 01. 배출 전 기록")
            st.write("순환의 시작을 사진으로 남겨주세요. AI가 적절한 분류 방법을 제안합니다.")
            img1 = st.camera_input("", key="cam1")
            if img1:
                if st.button("분석 시작하기"):
                    with st.spinner("이미지를 분석하고 있습니다..."):
                        try:
                            res = model.generate_content(["이 물건의 분리배출 핵심 팁을 2줄로 알려줘.", Image.open(img1)])
                            st.session_state.guide = res.text
                            st.session_state.step = 2
                            st.rerun()
                        except Exception as e: st.error(f"오류: {e}")

        elif st.session_state.step == 2:
            st.markdown(f"""
                <div style="background:rgba(45,90,39,0.05); padding:20px; border-radius:15px; margin-bottom:25px;">
                    <p style="margin:0; color:#2d5a27;"><b>🌱 AI의 가이드:</b> {st.session_state.guide}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("### 02. 실천 인증")
            st.write("안내에 따라 올바르게 분류된 모습을 보여주세요.")
            img2 = st.camera_input("", key="cam2")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("다시 시도"):
                    st.session_state.step = 1; st.rerun()
            with c2:
                if img2 and not st.session_state.verified:
                    if st.button("인증 완료"):
                        with st.spinner("실천 내용을 확인 중입니다..."):
                            try:
                                # 검수 로직 완화: 펼치기 같은 디테일보다 '분리배출 완료' 여부에 집중
                                res = model.generate_content(["가이드대로 적절히 분류하여 버릴 준비가 되었는지 확인해줘. 성공하면 반드시 '인증성공' 단어를 포함해줘.", Image.open(img2)])
                                if "인증성공" in res.text or "성공" in res.text:
                                    add_score()
                                    st.session_state.verified = True
                                    st.balloons(); st.success("소중한 실천이 기록되었습니다.")
                                else: st.error(f"확인 결과: {res.text}")
                            except Exception as e: st.error(f"오류: {e}")

        if st.session_state.verified:
            if st.button("새로운 기록 시작하기"):
                st.session_state.step = 1; st.session_state.verified = False; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:white; opacity:0.5; margin-top:50px;'>Nature Connect Project | 대지고등학교</p>", unsafe_allow_html=True)
