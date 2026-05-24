import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime

# --- [VIBE DESIGN] 애플&민트 스타일 커스텀 디자인 ---
st.set_page_config(page_title="대지고 탄소 다이어트", page_icon="🌱", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경색 - 연한 민트 */
    .stApp {
        background-color: #F0FFF4;
    }
    
    /* 제목 스타일 */
    .main-title {
        color: #2D3748;
        font-family: 'Pretendard', sans-serif;
        font-weight: 800;
        text-align: center;
        padding-top: 20px;
    }
    
    /* 점수판 카드 디자인 */
    .score-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid #C6F6D5;
    }
    
    /* 버튼 스타일 - 진한 초록 & 둥글게 */
    .stButton>button {
        width: 100%;
        background-color: #2F855A !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 12px 0px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        background-color: #276749 !important;
    }
    
    /* AI 분석 결과 박스 */
    .analysis-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #48BB78;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [CORE LOGIC] API 및 데이터 관리 ---

# API 키 설정 (Streamlit Secrets 필수)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🔑 Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 사용 가능한 모델 자동 찾기
@st.cache_resource
def get_ai_model():
    try:
        # 모델 목록을 가져와서 가장 적합한 것 선택
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = "gemini-1.5-flash" if "models/gemini-1.5-flash" in models else models[0]
        return genai.GenerativeModel(model_name)
    except:
        return None

model = get_ai_model()

# 점수 파일 관리
def load_score():
    if not os.path.exists("class_score.txt"):
        with open("class_score.txt", "w") as f: f.write("0")
    with open("class_score.txt", "r") as f:
        return int(f.read())

def update_score():
    new_score = load_score() + 1
    with open("class_score.txt", "w") as f:
        f.write(str(new_score))
    return new_score

# --- [SCREEN] 화면 구성 시작 ---

st.markdown("<h1 class='main-title'>🌱 대지고 탄소 다이어트</h1>", unsafe_allow_html=True)
st.write("<p style='text-align:center; color:#4A5568;'>우리 반의 실천으로 지구의 온도를 낮춰요!</p>", unsafe_allow_html=True)

# 1. 메인 점수판 게이지
current_score = load_score()
goal = 100

st.markdown(f"""
    <div class="score-card">
        <span style="color: #4A5568; font-size: 16px;">우리 반 누적 인증</span>
        <h2 style="color: #2F855A; margin: 5px 0;">{current_score}회</h2>
    </div>
    """, unsafe_allow_html=True)

st.progress(min(current_score / goal, 1.0))
st.caption(f"목표 100회까지 {max(goal - current_score, 0)}회 남았습니다! 🔥")

st.divider()

# 2. 사진 찍기 및 분석
st.subheader("📸 분리배출 인증샷")
img_file = st.camera_input("쓰레기 사진을 찍으면 AI가 분석해줍니다.")

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="인증 대기 중...", use_container_width=True)
    
    if st.button("AI 환경 전문가에게 물어보기 ✨"):
        if model:
            with st.spinner("AI 전문가가 꼼꼼하게 사진을 보는 중..."):
                try:
                    prompt = """
                    너는 학교 환경 교육 전문가야. 학생이 찍은 쓰레기 사진을 보고 다음 양식으로 아주 구체적으로 답해줘.
                    1. [진단]: 사진 속 물건이 무엇인지, 비닐 라벨이 붙어있는지, 이물질이 있는지 정확히 짚어줘. (예: '앗! 페트병에 비닐 라벨이 그대로 붙어있네요!')
                    2. [행동]: '이것은 [재질]로 분류되지만, 반드시 [어떤 행동]을 해야 합니다.'라는 핵심 문구를 포함해줘.
                    3. [응원]: 실천을 독려하는 따뜻한 응원 메시지 한 줄과 줄인 탄소량을 예측해서 적어줘.
                    """
                    response = model.generate_content([prompt, img])
                    
                    st.markdown(f"""
                        <div class="analysis-box">
                            <h4 style="margin-top:0; color:#2F855A;">📋 AI 분석 결과</h4>
                            {response.text}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 인증 버튼 (분석 후에만 등장)
                    st.write("")
                    if st.button("✅ 올바르게 배출했어요! 인증하기"):
                        new_total = update_score()
                        st.balloons() # 풍선 팡팡!
                        st.success(f"인증 성공! 우리 반의 점수가 {new_total}점이 되었습니다! 🎉")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했어요. 다시 시도해볼까요? (에러: {e})")
        else:
            st.error("AI 모델을 불러오지 못했습니다. API 키 설정을 확인해주세요.")

# 하단 푸터
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("© 2024 대지고등학교 2학년 환경 자치회 프로젝트 | Created with Vibe Coding")
