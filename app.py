import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. 보안 설정 (Secrets에서 키 가져오기) ---
if "GEMINI_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("🔑 API 키가 설정되지 않았습니다. Streamlit Cloud 설정의 Secrets 칸에 GEMINI_API_KEY를 입력해주세요.")
    st.stop()

# --- 2. 모델 설정 (에러 방지용 자동 선택) ---
@st.cache_resource
def load_model():
    try:
        # 사용 가능한 모델 중 gemini-1.5-flash를 최우선으로 선택
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro-vision') # 백업용

model = load_model()

# --- 3. 점수 저장 시스템 (파일 방식) ---
def get_score():
    if not os.path.exists("score.txt"):
        with open("score.txt", "w") as f: f.write("0")
    with open("score.txt", "r") as f: return int(f.read())

def save_score():
    current = get_score()
    with open("score.txt", "w") as f: f.write(str(current + 1))
    return current + 1

# --- 4. 웹 화면 구성 (UI) ---
st.set_page_config(page_title="우리 반 탄소 다이어트", page_icon="♻️")

st.title("♻️ AI 분리배출 가이드 & 탄소 다이어트")
st.write("대지고등학교 통합사회 프로젝트 - 사진을 찍어 분리배출을 인증하세요!")

# 점수 및 게이지 바
score = get_score()
st.subheader(f"📊 우리 반 누적 인증: {score}회")
st.progress(min(score / 100, 1.0)) # 100회 목표
st.write(f"목표까지 {100 - score}번 남았습니다. 파이팅! 🔥")

st.divider()

# 사진 입력 (카메라 + 파일 업로드)
img_file = st.camera_input("쓰레기 사진을 찍어주세요!")
if not img_file:
    img_file = st.file_uploader("또는 사진 파일을 올려주세요", type=['jpg', 'jpeg', 'png'])

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="입력된 사진", use_container_width=True)
    
    if st.button("AI 분리배출 분석 시작 ✨"):
        with st.spinner("AI가 분석 중입니다..."):
            try:
                # 구체적인 분석 요청
                prompt = """
                너는 환경 전문가야. 사진 속 쓰레기를 보고 아래 형식으로 답해줘:
                1. '이것은 [재질]로 분류되지만 [어떻게] 해야 합니다' 형식을 포함할 것.
                2. 비닐 라벨 제거 여부나 세척 필요성을 꼼꼼히 체크해줘.
                3. 마지막에 탄소 절감 효과를 한 줄로 적어줘.
                학생들에게 말하듯 친절하게 설명해줘.
                """
                response = model.generate_content([prompt, img])
                
                st.success("✅ 분석 완료!")
                st.info(response.text)
                
                # 분석 후에 나타나는 인증 버튼
                if st.button("실제로 실천했습니다! 점수 올리기 🚩"):
                    new_score = save_score()
                    st.balloons()
                    st.success(f"인증 성공! 현재 {new_score}점입니다.")
                    st.rerun()

            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

st.caption("© 2024 대지고등학교 환경 프로젝트 | Powered by Gemini 1.5 Flash")
