import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. API 키 설정 - 2개 키로 제한 방어] ---
def setup_ai():
    # 첫 번째 키 시도, 안되면 두 번째 키 사용
    keys = []
    if "GEMINI_API_KEY" in st.secrets: keys.append(st.secrets["GEMINI_API_KEY"])
    if "GEMINI_API_KEY_2" in st.secrets: keys.append(st.secrets["GEMINI_API_KEY_2"])
    
    if not keys:
        st.error("Secrets에 API 키를 등록해주세요!")
        st.stop()
    
    # 기본적으로 첫 번째 키 사용
    genai.configure(api_key=keys[0])
    return keys

api_keys = setup_ai()
# 1.5 Flash 최신 모델 (404 방지)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def call_gemini(prompt, image):
    try:
        return model.generate_content([prompt, image]).text
    except Exception as e:
        # 429(한도초과) 에러 발생 시 두 번째 키가 있다면 시도
        if "429" in str(e) and len(api_keys) > 1:
            genai.configure(api_key=api_keys[1])
            try:
                return model.generate_content([prompt, image]).text
            except:
                return "🚨 모든 API 키의 한도가 초과되었습니다. 1분만 기다려주세요!"
        return f"에러 발생: {e}"

# --- [디자인 및 UI는 이전과 동일] ---
st.set_page_config(page_title="Eco-Bot", page_icon="🤖")
st.title("🤖 에러 없는 Eco-Bot")

if 'step' not in st.session_state: st.session_state.step = 1

if st.session_state.step == 1:
    img = st.camera_input("사진을 찍어주세요")
    if img:
        if st.button("AI 분석 시작"):
            res = call_gemini("이 쓰레기 분리배출법 3줄 요약해줘.", Image.open(img))
            st.write(res)
            if "🚨" not in res:
                st.session_state.step = 2
                st.session_state.guide = res
