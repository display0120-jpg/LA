import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [DESIGN] 앱 디자인 세팅 ---
st.set_page_config(page_title="대지고 탄소 다이어트 V2", page_icon="♻️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F0FFF4; }
    .main-title { color: #2D3748; text-align: center; font-weight: 800; }
    .step-box { background-color: white; padding: 20px; border-radius: 15px; border: 2px solid #C6F6D5; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 15px !important; background-color: #2F855A !important; color: white !important; font-weight: 700 !important; height: 3em !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [LOGIC] API 및 세션 상태 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키를 설정해주세요!")
    st.stop()

# 2단계 인증을 위한 상태 기억장치
if 'step' not in st.session_state: st.session_state.step = 1  # 1: 진단, 2: 확인
if 'instructions' not in st.session_state: st.session_state.instructions = ""

model = genai.GenerativeModel('gemini-1.5-flash')

def load_score():
    if not os.path.exists("class_score.txt"): return 0
    with open("class_score.txt", "r") as f: return int(f.read())

def add_score():
    score = load_score() + 1
    with open("class_score.txt", "w") as f: f.write(str(score))
    return score

# --- [UI] 메인 화면 ---
st.markdown("<h1 class='main-title'>🌱 대지고 2단계 인증 챌린지</h1>", unsafe_allow_html=True)
score = load_score()
st.info(f"📊 우리 반 누적 인증: {score}회 | 100회까지 파이팅!")

# --- [STAGE 1] 쓰레기 진단 단계 ---
if st.session_state.step == 1:
    st.subheader("1️⃣ 1단계: 쓰레기 상태 진단")
    st.write("버리기 전 상태의 사진을 찍어주세요.")
    
    before_img = st.camera_input("전 사진 촬영", key="before_cam")
    
    if before_img:
        if st.button("분리배출 방법 알아보기 ✨"):
            with st.spinner("AI가 분석 중..."):
                img = Image.open(before_img)
                prompt = "이 쓰레기를 분리배출하기 위해 사용자가 '지금 당장 해야 할 구체적인 행동'을 알려줘. 예: 비닐 떼기, 씻기 등. 아주 짧고 명확하게!"
                response = model.generate_content([prompt, img])
                
                st.session_state.instructions = response.text
                st.session_state.step = 2
                st.rerun()

# --- [STAGE 2] 결과 확인 단계 ---
elif st.session_state.step == 2:
    st.subheader("2️⃣ 2단계: 미션 수행 인증")
    st.warning(f"🎯 미션: {st.session_state.instructions}")
    st.write("위 방법대로 분리수거를 마친 사진을 찍어주세요.")
    
    after_img = st.camera_input("후 사진 촬영", key="after_cam")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음부터 다시 찍기"):
            st.session_state.step = 1
            st.rerun()
            
    with col2:
        if after_img:
            if st.button("최종 인증 받기 ✅"):
                with st.spinner("미션을 잘 수행했는지 검사 중..."):
                    img = Image.open(after_img)
                    # 이전 지시사항을 바탕으로 검수 요청
                    verify_prompt = f"사용자에게 준 지시사항은 이거였어: '{st.session_state.instructions}'. 사진을 보고 지시사항대로 잘 처리됐는지 확인해줘. 잘 됐으면 '성공'이라는 단어를 포함해서 칭찬해주고, 안 됐으면 뭐가 부족한지 알려줘."
                    response = model.generate_content([verify_prompt, img])
                    
                    if "성공" in response.text or "통과" in response.text or "잘" in response.text:
                        add_score()
                        st.balloons()
                        st.success(f"축하합니다! 미션 완료! {response.text}")
                        if st.button("다음 쓰레기 인증하기"):
                            st.session_state.step = 1
                            st.rerun()
                    else:
                        st.error(f"앗! 조금 더 노력이 필요해요: {response.text}")

st.caption("대지고 환경 프로젝트 | 실천하는 당신이 아름답습니다.")
