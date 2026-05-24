import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. API 설정 (Secrets 사용) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

# --- 2. 404 에러 방지용 모델 로드 함수 (핵심 수정) ---
@st.cache_resource
def load_model():
    try:
        # 현재 API 버전에서 사용 가능한 모든 모델 목록을 가져와서 출력해봅니다 (로그 확인용)
        available_models = [m.name for m in genai.list_models()]
        
        # 우선순위대로 모델 체크
        if "models/gemini-1.5-flash" in available_models:
            return genai.GenerativeModel("gemini-1.5-flash")
        elif "models/gemini-1.5-pro" in available_models:
            return genai.GenerativeModel("gemini-1.5-pro")
        elif "models/gemini-pro-vision" in available_models:
            return genai.GenerativeModel("gemini-pro-vision")
        else:
            # 하나도 없다면 리스트의 첫 번째 모델이라도 가져옵니다.
            return genai.GenerativeModel(available_models[0].replace("models/", ""))
    except Exception as e:
        st.error(f"모델 로드 실패: {e}")
        return None

model = load_model()

# --- 3. 점수 관리 ---
def get_score():
    if not os.path.exists("score.txt"):
        with open("score.txt", "w") as f: f.write("0")
    try:
        with open("score.txt", "r") as f: return int(f.read())
    except: return 0

def save_score():
    current = get_score()
    with open("score.txt", "w") as f: f.write(str(current + 1))
    return current + 1

# --- 4. UI ---
st.title("♻️ 완벽한 AI 분리배출 가이드")
score = get_score()
st.subheader(f"📊 우리 반 점수: {score}점")
st.progress(min(score/100, 1.0))

img_file = st.camera_input("사진을 찍어주세요")

if img_file:
    img = Image.open(img_file)
    if st.button("AI 분석하기"):
        if model:
            with st.spinner("AI가 분석 중..."):
                try:
                    # 이미지 분석 시 프롬프트
                    prompt = "이 쓰레기를 어떻게 분리배출해야 할까? '이것은 [재질]이지만 [어떻게] 해야 합니다' 형식을 포함해서 설명해줘."
                    response = model.generate_content([prompt, img])
                    st.success("분석 완료!")
                    st.write(response.text)
                    
                    if st.button("점수 올리기!"):
                        save_score()
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"분석 중 오류: {e}")
        else:
            st.error("사용 가능한 AI 모델을 찾을 수 없습니다.")
