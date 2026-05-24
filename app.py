import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 브랜딩 & 디자인 세팅] ---
st.set_page_config(page_title="Eco-Bot 탄소 다이어트", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    /* 헤더 디자인 */
    .header-container {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        padding: 30px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 20px;
    }
    
    /* AI 로봇 카드 */
    .bot-card {
        background-color: white; padding: 20px; border-radius: 20px;
        border: 2px solid #D1FAE5; margin-bottom: 20px;
        display: flex; align-items: center; gap: 15px;
    }
    .bot-icon { font-size: 40px; }
    
    /* 미션 카드 */
    .mission-card {
        background-color: #ECFDF5; padding: 15px; border-radius: 15px;
        border-left: 5px solid #10B981; margin: 10px 0;
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [2. AI 및 상태 관리] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키를 등록해주세요!")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# 세션 상태 초기화 (메시지 꼬임 방지)
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verify_res' not in st.session_state: st.session_state.verify_res = None

def reset_app():
    st.session_state.step = 1
    st.session_state.guide = ""
    st.session_state.verify_res = None
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

# --- [3. 메인 UI] ---

st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 28px;">🤖 Eco-Bot 챌린지</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">우리 반 탄소 다이어트 가이드</p>
    </div>
    """, unsafe_allow_html=True)

score = load_score()
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="background:#D1FAE5; padding:5px 15px; border-radius:20px; color:#065F46; font-weight:700;">
            🔥 현재 우리 반 점수: {score}점
        </span>
    </div>
    """, unsafe_allow_html=True)

# --- [4. 2단계 로직] ---

if st.session_state.step == 1:
    st.markdown("""
        <div class="bot-card">
            <div class="bot-icon">🤖</div>
            <div>
                <strong>안녕! 나는 에코봇이야.</strong><br>
                버리기 전 쓰레기 사진을 찍어주면 방법을 알려줄게!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    img1 = st.camera_input("버리기 전 사진 찍기", key="cam1")
    
    if img1:
        if st.button("AI 가이드 받기 ✨"):
            with st.spinner("에코봇이 분석 중..."):
                try:
                    # 가이드를 아주 간단하게 요청
                    prompt = "이 쓰레기를 분리배출하는 법을 '1.비움 2.제거 3.분류' 형태로 아주 짧게 3줄로만 요약해줘."
                    res = model.generate_content([prompt, Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e: st.error(f"분석 실패: {e}")

elif st.session_state.step == 2:
    st.markdown(f"""
        <div class="bot-card">
            <div class="bot-icon">💡</div>
            <div>
                <strong>미션을 확인하고 실천해봐!</strong>
            </div>
        </div>
        <div class="mission-card">
            {st.session_state.guide}
        </div>
    """, unsafe_allow_html=True)
    
    img2 = st.camera_input("실천 후 사진 찍기", key="cam2")
    
    if st.button("다시 처음부터 하기 🔄"):
        reset_app()

    if img2:
        if st.button("실천 완료 인증하기 ✅"):
            with st.spinner("잘 했는지 검사 중..."):
                try:
                    verify_prompt = f"사용자 미션: {st.session_state.guide}. 이 사진이 미션을 잘 지켰니? 잘 했으면 딱 한 문장으로 '성공! 정말 깨끗하네요'라고 하고, 안 됐으면 '실패! 비닐을 더 제거하세요'라고 짧게 말해줘."
                    res = model.generate_content([verify_prompt, Image.open(img2)])
                    st.session_state.verify_res = res.text
                    
                    if "성공" in res.text:
                        add_score()
                        st.balloons()
                        st.success(res.text)
                        if st.button("다음 쓰레기 하러 가기"):
                            reset_app()
                    else:
                        st.error(res.text)
                        st.info("부족한 부분을 보완해서 다시 찍어줘!")
                except Exception as e: st.error(f"검증 오류: {e}")

st.markdown("---")
st.caption("대리고등학교 2학년 환경 프로젝트 | Eco-Bot v1.2")
