import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 보안 및 API 설정] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# --- [2. 404 에러 원천 차단 모델 로더] ---
@st.cache_resource
def get_safe_model():
    try:
        # 내 API 키로 사용 가능한 모델 목록을 전부 가져옵니다.
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 우선순위에 따라 모델 선택 (404 방지용 정밀 타겟팅)
        if "models/gemini-1.5-flash" in available_models:
            return genai.GenerativeModel("gemini-1.5-flash")
        elif "models/gemini-1.5-flash-latest" in available_models:
            return genai.GenerativeModel("gemini-1.5-flash-latest")
        elif "models/gemini-pro-vision" in available_models:
            return genai.GenerativeModel("gemini-pro-vision")
        else:
            # 하나도 없다면 리스트 중 첫 번째 작동하는 모델 선택
            return genai.GenerativeModel(available_models[0].replace("models/", ""))
    except Exception as e:
        st.error(f"모델을 불러오는 중 오류 발생: {e}")
        return None

model = get_safe_model()

# --- [3. 앱 상태 관리 (2단계 인증용)] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'mission' not in st.session_state: st.session_state.mission = ""

def load_score():
    if not os.path.exists("score.txt"): return 0
    with open("score.txt", "r") as f: return int(f.read())

def add_score():
    score = load_score() + 1
    with open("score.txt", "w") as f: f.write(str(score))
    return score

# --- [4. 디자인 및 화면 구성] ---
st.set_page_config(page_title="대지고 탄소 다이어트", layout="centered")
st.markdown("<style>.stApp {background-color: #F7FAFC;}</style>", unsafe_allow_html=True)

st.title("♻️ 대지고 2단계 실천 인증")
score = load_score()
st.subheader(f"📊 우리 반 누적 인증: {score}점")
st.progress(min(score/100, 1.0))

st.divider()

# --- [5. 메인 로직: 2단계 프로세스] ---

if st.session_state.step == 1:
    st.subheader("1️⃣ 단계: 분리배출 방법 진단")
    st.write("버리기 전 쓰레기 사진을 찍으세요.")
    img1 = st.camera_input("전 사진", key="cam1")
    
    if img1:
        if st.button("AI에게 배출 방법 물어보기 ✨"):
            with st.spinner("AI 분석 중..."):
                try:
                    res = model.generate_content(["이 쓰레기를 깨끗이 분리배출하기 위해 내가 지금 당장 해야 할 '단 한 가지 행동'을 15자 이내로 말해줘. (예: 비닐 라벨 떼기, 내용물 씻기)", Image.open(img1)])
                    st.session_state.mission = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"분석 오류: {e}")

elif st.session_state.step == 2:
    st.subheader("2️⃣ 단계: 실천 완료 인증")
    st.info(f"🎯 미션: **{st.session_state.mission}**")
    st.write("위 작업을 완료한 후의 깨끗한 사진을 찍으세요.")
    
    img2 = st.camera_input("후 사진", key="cam2")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음부터 다시하기"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if img2:
            if st.button("최종 확인 및 인증 ✅"):
                with st.spinner("미션 수행 검토 중..."):
                    try:
                        # 검증 로직
                        verify_prompt = f"사용자에게 준 미션은 '{st.session_state.mission}'이었어. 이 사진이 미션을 잘 수행한 결과물인지 확인해줘. 잘 됐으면 '인증성공'이라는 단어를 포함해서 칭찬해줘."
                        res = model.generate_content([verify_prompt, Image.open(img2)])
                        
                        if "인증성공" in res.text or "성공" in res.text or "잘" in res.text:
                            add_score()
                            st.balloons()
                            st.success(f"대단해요! {res.text}")
                            if st.button("다음 쓰레기 인증하기"):
                                st.session_state.step = 1
                                st.rerun()
                        else:
                            st.error(f"미션이 아직 부족해요: {res.text}")
                    except Exception as e:
                        st.error(f"검증 중 오류: {e}")
