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

# 하루 1,500회 무료인 안정적인 1.5 Flash 모델 사용
model = genai.GenerativeModel('gemini-1.5-flash')

# --- [2. 고대비 디자인 및 에코룡 배치 세팅] ---
st.set_page_config(page_title="에코룡의 지구 구출 작전", page_icon="🦖", layout="wide")

# 로컬 이미지를 웹에서 보여주기 위해 Base64로 변환하는 함수
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

ecoryong_img = get_base64_image("ecoryong.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@900&display=swap');

    /* 배경: 숲 배경 고정 */
    .stApp {{
        background: url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* 가독성 핵심: 검정 글씨 + 두꺼운 흰색 테두리 (text-shadow 8방향) */
    h1, h2, h3, h4, p, span, label, .stMarkdown, .info-text {{
        color: #000000 !important;
        font-family: 'Pretendard', sans-serif !important;
        font-weight: 900 !important;
        text-shadow: 
            -3px -3px 0 #fff,  
             3px -3px 0 #fff,
            -3px  3px 0 #fff,
             3px  3px 0 #fff,
             0px -3px 0 #fff,
             0px  3px 0 #fff,
            -3px  0px 0 #fff,
             3px  0px 0 #fff,
             2px 2px 10px rgba(0,0,0,0.2) !important;
    }}

    /* 사이트 메인 제목 */
    .main-title {{
        font-family: 'Black Han Sans', sans-serif !important;
        font-size: 5.5rem !important;
        text-align: center;
        margin-top: 0px;
        line-height: 1.1;
        color: #000 !important;
    }}

    /* 에코룡 캐릭터 (보내주신 이미지 그대로 좌측 하단 배치) */
    .ecoryong-container {{
        position: fixed;
        bottom: -30px;
        left: 20px;
        width: 420px;
        z-index: 999;
        pointer-events: none;
    }}
    
    .speech-bubble {{
        position: fixed;
        bottom: 380px;
        left: 120px;
        background: #ffffff;
        color: #059669 !important;
        padding: 25px 35px;
        border-radius: 50px;
        border: 6px solid #059669;
        font-weight: 900 !important;
        font-size: 1.7rem;
        z-index: 1000;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.1);
        text-shadow: none !important; /* 말풍선 안은 테두리 제거 */
    }}

    /* 점수판 (노란색 상자) */
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

    /* 버튼 스타일 */
    .stButton>button {{
        background: #059669 !important;
        color: white !important;
        border: 4px solid white !important;
        border-radius: 30px !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        height: 110px !important;
        width: 100% !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4) !important;
        text-shadow: none !important;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        background: #065f46 !important;
    }}

    /* 카메라 입력 스타일 */
    .stCameraInput {{
        border: 6px solid white !important;
        border-radius: 30px !important;
    }}
    </style>
    
    <div class="speech-bubble">안녕! 난 지구 구출 대장<br>에코룡이야! 같이 해볼래? 🦖</div>
    <div class="ecoryong-container">
        <img src="data:image/png;base64,{ecoryong_img}" width="100%">
    </div>
    """, unsafe_allow_html=True)

# --- [3. 점수 및 데이터 저장 로직] ---
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

# --- [4. 메인 화면 구성] ---
score = load_score()
st.markdown(f'<div class="score-badge">🏆 {score}점</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">에코룡의<br>지구 구출 작전</h1>', unsafe_allow_html=True)

# 레이아웃 정렬용 컬럼
_, col_main, _ = st.columns([1, 4, 1])

with col_main:
    # 1단계
    if st.session_state.step == 1:
        st.markdown("### 📸 1단계: 배출 전 상태 촬영")
        st.markdown("<p style='font-size:1.6rem;'>버리기 전의 사진을 찍어줘!<br>에코룡이 깐깐하게 방법을 알려줄게.</p>", unsafe_allow_html=True)
        img1 = st.camera_input("", key="cam1")
        if img1:
            if st.button("에코룡, 배출법을 알려줘! 💡"):
                with st.spinner("에코룡이 분석 중..."):
                    try:
                        res = model.generate_content(["이 물건 분리배출법 3줄 요약. 특히 우유팩은 씻어서 펼쳐야 한다고 강조해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류 발생: {e}")

    # 2단계
    elif st.session_state.step == 2:
        st.markdown("### 📝 에코룡의 지시사항")
        st.markdown(f"<div style='background:rgba(255,255,255,0.3); padding:20px; border-radius:20px;'><p style='font-size:1.6rem;'>{st.session_state.guide}</p></div>", unsafe_allow_html=True)
        
        st.markdown("### ✅ 2단계: 실천 인증 촬영")
        st.markdown("<p style='font-size:1.6rem;'>가이드대로 했지? 우유팩을 안 펼쳤으면 가차없이 탈락이야!</p>", unsafe_allow_html=True)
        img2 = st.camera_input("", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("인증 완료! ✅"):
                    with st.spinner("에코룡이 현미경 검토 중..."):
                        try:
                            verify_prompt = f"""
                            가이드: {st.session_state.guide}
                            너는 세계 최고의 분리배출 감독관 '에코룡'이야.
                            [검사 규칙]
                            1. 우유팩/종이상자: 반드시 평평하게 '펼쳐져' 있어야 함. 입체적이면 무조건 '인증실패'.
                            2. 페트병: 라벨이 제거되어야 함.
                            완벽하면 '인증성공'이라 말하고 칭찬해줘.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"판정 결과: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 작전 수행하기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

st.markdown("<p style='text-align:center; margin-top:100px; font-size:1.3rem;'>대지고등학교 환경 지킴이 | 캐릭터: 에코룡</p>", unsafe_allow_html=True)
