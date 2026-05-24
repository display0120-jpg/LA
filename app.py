import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. API 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# --- [2. 디자인 세팅 (글씨가 무조건 보이게)] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🦖", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Pretendard:wght@800;900&display=swap');

    /* 배경: 숲 사진은 유지하되, 전체적으로 흐리게(Blur) 처리하여 글씨에 집중 */
    .stApp {
        background: url("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-1.2.1&auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 상단 제목 섹션: 흰색 박스를 깔아서 무조건 보이게 함 */
    .header-box {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 5px solid #059669;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    .header-box h1 {
        font-family: 'Black Han Sans', sans-serif;
        font-size: 4rem;
        color: #059669;
        margin: 0;
    }

    /* 메인 컨텐츠 카드: 완전 불투명한 흰색 배경 사용 (가독성 100%) */
    .main-container {
        background: #ffffff !important;
        border-radius: 30px;
        padding: 40px;
        border: 8px solid #059669;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        margin: 0 auto;
        max-width: 800px;
        color: #000000 !important; /* 모든 글씨 검정색 */
    }

    /* 모든 텍스트 강제 검정색 및 굵게 */
    .stMarkdown, .stText, p, span, label {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.2rem;
    }

    /* 캐릭터 에코룡 (화면 좌측 하단 고정) */
    .mascot-img {
        position: fixed;
        bottom: -20px;
        left: 20px;
        width: 320px;
        z-index: 9999;
    }
    
    .speech-bubble {
        position: fixed;
        bottom: 280px;
        left: 60px;
        background: #fde047;
        color: black;
        padding: 20px;
        border-radius: 20px;
        border: 4px solid black;
        font-family: 'Pretendard', sans-serif;
        font-weight: 900;
        z-index: 10000;
        width: 220px;
        box-shadow: 5px 5px 0px rgba(0,0,0,0.2);
    }

    /* 점수판: 노란색 고대비 박스 */
    .score-badge {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fde047;
        color: black;
        padding: 15px 30px;
        border: 4px solid black;
        border-radius: 15px;
        font-family: 'Black Han Sans', sans-serif;
        font-size: 1.8rem;
        z-index: 1000;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background: #059669 !important;
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        border: 4px solid black !important;
        height: 80px !important;
    }
    </style>
    
    <!-- 캐릭터와 말풍선 -->
    <div class="speech-bubble">거기 너! 우유팩 펼쳤어? 안 펼치면 에코룡이 쫓아간다! 🦖</div>
    <img src="https://cdni.iconscout.com/illustration/premium/thumb/cute-dinosaur-illustration-download-in-svg-png-gif-file-formats--monster-character-green-pack-fantasy-illustrations-5386057.png" class="mascot-img">
    """, unsafe_allow_html=True)

# --- [3. 데이터 및 상태 로직] ---
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
st.markdown(f'<div class="score-badge">🏆 점수: {score}점</div>', unsafe_allow_html=True)

# 헤더 섹션
st.markdown('<div class="header-box"><h1>♻️ Eco-Bot 챌린지</h1></div>', unsafe_allow_html=True)

# 중앙 컨텐츠
col_l, col_m, col_r = st.columns([1, 5, 1])

with col_m:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    if st.session_state.step == 1:
        st.markdown("### 📸 1단계: 원래 상태 찍기")
        st.write("버리기 전 사진을 찍으세요. 에코룡이 방법을 알려줄게요.")
        img1 = st.camera_input("촬영하기", key="cam1")
        if img1:
            if st.button("에코룡에게 물어보기 💡"):
                with st.spinner("에코룡이 분석 중..."):
                    try:
                        res = model.generate_content(["이 쓰레기 분리배출법 3줄 요약해줘. 특히 우유팩은 반드시 펼치라고 말해줘.", Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    elif st.session_state.step == 2:
        st.markdown(f"""
            <div style="background:#f0fdf4; padding:20px; border-radius:15px; border:4px solid #059669; margin-bottom:20px;">
                <h4 style="color:#059669; margin-top:0;">📝 에코룡의 지시사항</h4>
                <p style="color:black;">{st.session_state.guide}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✅ 2단계: 실천 인증하기")
        st.write("우유팩은 쫙 펼치고, 라벨은 다 뗐나요? 제대로 안 하면 실패입니다!")
        img2 = st.camera_input("인증샷 찍기", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("다시 찍기 🔄"):
                st.session_state.step = 1; st.rerun()
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("에코룡에게 인증받기! ✅"):
                    with st.spinner("현미경 검사 중..."):
                        try:
                            # 깐깐한 프롬프트
                            verify_prompt = f"""
                            가이드: {st.session_state.guide}
                            사진을 보고 다음을 검사해. 
                            1. 우유팩은 무조건 평평하게 펼쳐져 있어야 함. 입체적이면 무조건 '인증실패'.
                            2. 페트병은 라벨이 제거되어야 함.
                            완벽하면 '인증성공'이라 말해줘.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"실패: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

    if st.session_state.verified:
        if st.button("다음 미션 하러 가기 ➡️"):
            st.session_state.step = 1
            st.session_state.verified = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
