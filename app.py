import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. API 설정 ---
# 팁: 보안을 위해 Streamlit의 Secrets 기능을 쓰는 것이 좋지만, 우선 작동 확인을 위해 직접 넣으세요.
GOOGLE_API_KEY = "AIzaSyDGZLjbc6oczqHhT_nMuXIj_1--OHKowGI"
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. 모델 자동 선택 시스템 (404 에러 방지 핵심) ---
@st.cache_resource
def load_working_model():
    try:
        # 사용 가능한 모델 목록을 가져옵니다.
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1순위: gemini-1.5-flash, 2순위: gemini-1.5-pro, 3순위: 아무거나 첫번째
        target_model = ""
        if "models/gemini-1.5-flash" in available_models:
            target_model = "gemini-1.5-flash"
        elif "models/gemini-1.5-pro" in available_models:
            target_model = "gemini-1.5-pro"
        else:
            # "models/" 접두사를 떼고 이름만 추출
            target_model = available_models[0].split('/')[-1]
            
        return genai.GenerativeModel(target_model)
    except Exception as e:
        st.error(f"모델 목록을 불러오는데 실패했습니다. API 키가 활성화되었는지 확인하세요: {e}")
        return None

model = load_working_model()

# --- 3. 데이터 저장 기능 ---
def get_score():
    if not os.path.exists("score.txt"):
        with open("score.txt", "w") as f: f.write("0")
    with open("score.txt", "r") as f: return int(f.read())

def save_score():
    current = get_score()
    with open("score.txt", "w") as f: f.write(str(current + 1))
    return current + 1

# --- 4. 웹 UI 구성 ---
st.set_page_config(page_title="우리 반 탄소 다이어트", page_icon="♻️")
st.title("♻️ AI 분리배출 가이드")

# 점수판
score = get_score()
st.subheader(f"📊 우리 반 누적 인증: {score}회")
st.progress(min(score / 100, 1.0))

st.divider()

# 사진 촬영 및 업로드
img_file = st.camera_input("쓰레기 사진을 찍어주세요!")

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="촬영된 사진", use_container_width=True)
    
    if st.button("AI 분석 시작"):
        if model is None:
            st.error("사용 가능한 AI 모델이 없습니다. API 키를 확인해 주세요.")
        else:
            with st.spinner("AI가 분석 중입니다... 잠시만 기다려 주세요."):
                try:
                    # 프롬프트 설정
                    prompt = "이 사진 속 물건의 분리배출 방법을 '이것은 [재질]로 분류되지만 [어떻게] 해야 합니다'라는 문구와 함께 친절히 알려줘. 탄소 절감 효과도 꼭 포함해줘."
                    
                    # 분석 요청 (이미지 처리 방식 최신화)
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.success("✅ AI 분석 결과")
                        st.info(response.text)
                        
                        # 분석 성공시에만 인증 버튼 노출
                        if st.button("실제로 분리수거 완료! 점수 올리기"):
                            new_score = save_score()
                            st.balloons()
                            st.rerun()
                    else:
                        st.warning("AI가 답변을 생성하지 못했습니다. 다시 시도해 주세요.")
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("도움말: 사진 용량이 너무 크거나 인터넷 연결이 불안정할 수 있습니다.")

st.caption("대지고등학교 통합사회 프로젝트 | 💡 Powered by Google Gemini")
