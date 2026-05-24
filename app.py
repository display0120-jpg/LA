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

# 404 에러 방지: 가장 최신 버전의 모델 호출 방식을 사용합니다.
@st.cache_resource
def load_stable_model():
    try:
        # v1beta 대신 최신 API를 사용하도록 유도하는 표준 이름 사용
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"모델 로드 중 오류가 발생했습니다: {e}")
        return None

model = load_stable_model()

# --- [2. 이미지 로드 로직 (에코룡 캐릭터)] ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

ecoryong_base64 = get_base64_image("ecoryong.png")
# 이미지가 있으면 사용자 이미지, 없으면 예비 아이콘 사용
mascot_src = f"data:image/png;base64,{ecoryong_base64}" if ecoryong_base64 else "https://cdn-icons-png.flaticon.com/512/2312/2312218.png"

# --- [3. 디자인 (에코룡/말풍선 위치 및 가독성 고정)] ---
st.set_page_config(page_title="에코룡의 지구 구출 작전", page_icon="🦖", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@900&display=swap');

    /* 배경 설정 */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.15), rgba(0,0,0,0.15)),
                    url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* 고대비 텍스트: 검정 글씨 + 굵은 흰색 테두리 */
    h1, h2, h3, h4, p, span, label, .stMarkdown, .info-text {{
        color: #000000 !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 900 !important;
        text-shadow: 
            -3px -3px 0 #fff,  3px -3px 0 #fff,
            -3px  3px 0 #fff,  3px  3px 0 #fff,
             0px -3px 0 #fff,  0px  3px 0 #fff,
            -3px  0px 0 #fff,  3px  0px 0 #fff,
             2px 2px 10px rgba(0,0,0,0.3) !important;
    }}

    .main-title {{
        font-family: 'Black Han Sans', sans-serif !important;
        font-size: 5.5rem !important;
        text-align: center;
        margin-top: 0px;
        line-height: 1.1;
    }}

    /* 에코룡 위치: 살짝 왼쪽 아래 (-65px, -30px) */
    .ecoryong-container {{
        position: fixed;
        bottom: -65px; 
        left: -30px; 
        width: 450px;
        z-index: 999;
        pointer-events: none;
    }}
    
    /* 말풍선 위치: 왼쪽 위 (bottom: 480px, left: 20px) */
    .speech-bubble {{
        position: fixed;
        bottom: 480px; 
        left: 20px;   
        background: #ffffff;
        color: #059669 !important;
        padding: 20px 30px;
        border-radius: 50px;
        border: 6px solid #059669;
        font-weight: 900 !important;
        font-size: 1.6rem;
        z-index: 1000;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.1);
        text-shadow: none !important;
    }}

    .score-badge {{
        position: fixed;
        top: 30px;
        right: 40px;
        background: #fde047;
        color: black !important;
        padding: 20px 40px;
        border: 5px solid black;
        border-radius: 20px;
        font-family: 'Black Han Sans', sans-serif !important;
        font-size: 2.5rem;
        transform: rotate(3deg);
        z-index: 1000;
        text-shadow: none !important;
    }}

    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 4px solid white !important;
        border-radius: 30px !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        height: 100px !important;
        width: 100% !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important;
        text-shadow: none !important;
    }}
    </style>
    
    <div class="speech-bubble">안녕! 난 지구 구출 대장<br>에코룡이야! 준비됐어? 🦖</div>
    <div class="ecoryong-container">
        <img src="{mascot_src}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [4. 데이터 및 점수 로직] ---
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

# --- [5. 메인 UI 구성] ---
score = load_score()
st.markdown(f'<div class="score-badge">🏆 {score}점</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">에코룡의<br>지구 구출 작전</h1>', unsafe_allow_html=True)

_, col_main, _ = st.columns([1, 4, 1])

with col_main:
    if not model:
        st.error("AI 모델을 초기화하지 못했습니다. 잠시 후 새로고침 해주세요.")
        st.stop()

    if st.session_state.step == 1:
        st.markdown("### 📸 1단계: 배출 전 사진 촬영")
        img1 = st.camera_input("", key="cam1")
        if img1:
            if st.button("에코룡, 어떻게 버려? 💡"):
                with st.spinner("에코룡이 분석 중..."):
                    try:
                        res = model.generate_content(["이 물건 분리배출법 3줄 요약해줘. 특히 우유팩은 씻어서 펼쳐야 한다고 강조해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e:
                        if "429" in str(e): st.error("🚨 한도 초과! 1분만 기다려주세요.")
                        else: st.error(f"오류: {e}")

    elif st.session_state.step == 2:
        st.markdown(f"<div style='background:rgba(255,255,255,0.3); padding:20px; border-radius:20px;'><p style='font-size:1.6rem;'>{st.session_state.guide}</p></div>", unsafe_allow_html=True)
        st.markdown("### ✅ 2단계: 실천 인증샷 촬영")
        img2 = st.camera_input("", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("인증 완료! ✅"):
                    with st.spinner("현미경 검토 중..."):
                        try:
                            res = model.generate_content([f"가이드: {st.session_state.guide}. 사진을 보고 미션을 완벽히 했는지 확인해. 잘 했으면 '인증성공'이라 말해.", Image.open(img2)])
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons(); st.success(res.text)
                            else: st.error(f"판정 결과: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 작전 수행 ➡️"):
            st.session_state.step = 1; st.session_state.verified = False; st.rerun()

st.markdown("<p style='text-align:center; margin-top:100px; font-size:1.3rem;'>대지고등학교 환경 지킴이 | 캐릭터: 에코룡</p>", unsafe_allow_html=True)
