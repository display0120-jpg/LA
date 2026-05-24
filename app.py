import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 브랜딩 & 디자인 세팅] ---
st.set_page_config(page_title="Eco-Class 탄소 다이어트", page_icon="🌱", layout="centered")

# 고급스러운 그린/민트 테마 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stApp { background-color: #F0FFF4; }
    
    /* 상단 앱 배너 디자인 */
    .app-header {
        background: linear-gradient(135deg, #2D6A4F 0%, #40916C 100%);
        padding: 40px;
        border-radius: 0 0 40px 40px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* 카드 디자인 */
    .info-card {
        background-color: white;
        padding: 25px;
        border-radius: 25px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        border: 1px solid #D1FAE5;
        margin-bottom: 20px;
    }
    
    /* 강조 텍스트 */
    .highlight { color: #1B4332; font-weight: 800; font-size: 22px; }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%; border-radius: 20px !important;
        background-color: #2D6A4F !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important;
        border: none !important; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- [2. AI 및 데이터 로직] ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_safe_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = "gemini-1.5-flash" if "models/gemini-1.5-flash" in available else available[0]
        return genai.GenerativeModel(name)
    except: return None

model = get_safe_model()

# 상태 관리 및 점수
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [3. 메인 UI 화면] ---

# 앱 상단 로고/배너
st.markdown("""
    <div class="app-header">
        <h1 style="margin:0; font-size: 32px;">🌿 Eco-Class</h1>
        <p style="margin:10px 0 0 0; opacity: 0.9;">우리 반의 탄소 다이어트 챌린지</p>
    </div>
    """, unsafe_allow_html=True)

# 점수판 섹션
score = load_score()
st.markdown(f"""
    <div class="info-card" style="text-align: center;">
        <p style="margin:0; color:#52B788; font-weight:700;">현재 우리 반 점수</p>
        <div class="highlight">{score} Point</div>
        <div style="margin-top:10px; background:#ECFDF5; border-radius:10px; padding:5px;">
            목표 100회 중 {score}% 달성! 🌱
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- [4. 2단계 실천 로직] ---

if st.session_state.step == 1:
    st.markdown("### 📸 STEP 1. 분리배출 전 상태 진단")
    st.write("버리기 전의 쓰레기 사진을 찍어주세요. AI가 완벽한 가이드를 드립니다.")
    img1 = st.camera_input("전 사진 촬영", key="step1_cam")
    
    if img1:
        if st.button("전문가 가이드 확인하기 ✨"):
            with st.spinner("AI가 쓰레기 상태를 정밀 분석 중..."):
                try:
                    prompt = """
                    너는 대한민국 최고의 분리배출 전문가야. 사진을 보고 아래 항목을 꼼꼼히 분석해줘.
                    1. [물건 정보]: 사진 속 쓰레기가 무엇인지 정확히 명칭을 말해줘.
                    2. [체크리스트]: 페트병이라면 '비닐 라벨 제거', '뚜껑 분리', '내용물 세척', '찌그러뜨리기' 등 이 물건을 버리기 위해 해야 할 모든 행동을 번호를 매겨서 구체적으로 알려줘.
                    3. [탄소 절감]: 이 실천으로 줄일 수 있는 탄소량을 언급해줘.
                    아주 친절하고 깐깐하게 알려줘!
                    """
                    res = model.generate_content([prompt, Image.open(img1)])
                    st.session_state.guide = res.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e: st.error(f"분석 실패: {e}")

elif st.session_state.step == 2:
    st.markdown("### ✅ STEP 2. 실천 인증 완료")
    st.markdown(f"""
        <div class="info-card" style="border-left: 8px solid #2D6A4F;">
            <h4 style="margin:0; color:#2D6A4F;">🎯 오늘의 분리배출 미션</h4>
            <div style="margin-top:10px; font-size:15px; line-height:1.6;">
                {st.session_state.guide}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("위의 가이드대로 처리를 마친 깨끗한 사진을 찍어주세요!")
    img2 = st.camera_input("인증 사진 촬영", key="step2_cam")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음부터 다시하기 🔄"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if img2:
            if st.button("최종 인증 및 점수 획득! 🚩"):
                with st.spinner("실천 결과를 검토 중..."):
                    try:
                        verify_prompt = f"사용자에게 준 미션은 '{st.session_state.guide}'였어. 사진을 보고 비닐 라벨이 잘 제거됐는지, 내용물이 깨끗한지 확인해줘. 완벽하면 '인증성공'이라는 단어를 넣어서 축하해주고, 부족하면 다시 하라고 말해줘."
                        res = model.generate_content([verify_prompt, Image.open(img2)])
                        
                        if "인증성공" in res.text or "성공" in res.text or "축합" in res.text:
                            add_score()
                            st.balloons()
                            st.success(f"축하합니다! 미션 완료! \n\n{res.text}")
                            if st.button("다음 물건 인증하기"):
                                st.session_state.step = 1
                                st.rerun()
                        else:
                            st.error(f"앗! 아직 미션이 덜 끝난 것 같아요: \n\n{res.text}")
                    except Exception as e: st.error(f"검증 오류: {e}")

st.markdown("---")
st.caption("대지고등학교 환경 실천 자치회 | 본 앱은 인공지능에 의해 실시간 가이드를 제공합니다.")
