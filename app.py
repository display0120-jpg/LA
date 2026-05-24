import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 제미나이 API 설정 (무료 티어: gemini-1.5-flash 추천)
GOOGLE_API_KEY = "AIzaSyDGZLjbc6oczqHhT_nMuXIj_1--OHKowGI"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 인증 횟수 저장/불러오기 기능 (파일 하나로 끝내기 위해 단순하게 구현)
def get_count():
    if not os.path.exists("counter.txt"):
        with open("counter.txt", "w") as f: f.write("0")
    with open("counter.txt", "r") as f:
        return int(f.read())

def add_count():
    count = get_count() + 1
    with open("counter.txt", "w") as f:
        f.write(str(count))
    return count

# --- 웹 화면 구성 (하나의 파일에서 모두 처리) ---
st.set_page_config(page_title="우리 반 탄소 다이어트", page_icon="♻️")

st.title("♻️ AI 분리배출 가이드")
st.write("사진을 찍으면 AI가 분리배출 상태를 점검해줍니다.")

# 섹션 1: 우리 반 점수 게이지
score = get_count()
st.subheader(f"📊 우리 반 누적 인증: {score}회")
st.progress(min(score / 100, 1.0)) # 100회 목표

st.divider()

# 섹션 2: AI 사진 분석
# camera_input을 쓰면 폰에서 바로 카메라가 켜집니다!
img_file = st.camera_input("쓰레기 사진을 찍어주세요")

if img_file is not None:
    img = Image.open(img_file)
    
    with st.spinner("제미나이 AI가 분석 중..."):
        # AI에게 줄 구체적인 지시(프롬프트)
        prompt = """
        너는 환경 교육 전문가야. 이 사진 속의 쓰레기를 보고 다음을 알려줘:
        1. 사진 속 물건의 상태 진단 (예: 비닐이 안 떼어졌는지, 음식물이 묻었는지)
        2. '이것은 [재질]로 분류되지만, [구체적 행동요령]해야 합니다'라는 핵심 문구 포함.
        3. 제대로 배출했을 때의 탄소 절감 효과 한 줄.
        친절하고 격려하는 말투로 답변해줘.
        """
        
        # 제미나이에 이미지와 프롬프트 전달
        response = model.generate_content([prompt, img])
        
        st.success("✅ 분석 완료!")
        st.write(response.text)
        
        # 인증 버튼 (누르면 파일에 점수 저장 및 화면 새로고침)
        if st.button("실천 완료! 점수 올리기"):
            new_score = add_count()
            st.balloons()
            st.success(f"축하합니다! 현재 우리 반 점수: {new_score}")
            # 새로고침을 위해 코드 재실행
            st.rerun()

# 하단 정보
st.caption("대지고등학교 - 통합사회 II. 인간과 환경 프로젝트")