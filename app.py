import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1. 기본 설정 및 AI 연결] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🌿", layout="wide")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

@st.cache_resource
def get_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(target)
    except: return None

model = get_model()

# --- [2. 역대급 자연 테마 디자인 (CSS)] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    
    /* 전체 배경: 은은한 숲의 감성 */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80");
        background-attachment: fixed;
        background-size: cover;
        font-family: 'Pretendard', sans-serif;
    }

    /* 반투명 글래스모피즘 컨테이너 */
    .main-box {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        margin: 20px auto;
        max-width: 900px;
    }

    /* 상단 헤더 섹션 */
    .header-text {
        text-align: center;
        color: #064e3b;
        margin-bottom: 30px;
    }
    
    .header-text h1 { font-size: 3rem; font-weight: 700; color: #065f46; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .header-text p { font-size: 1.2rem; color: #047857; font-weight: 400; }

    /* 버튼 스타일 커스텀 */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px 30px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(5, 150, 105, 0.3);
    }

    /* 가이드 박스 */
    .guide-card {
        background: rgba(16, 185, 129, 0.1);
        border-radius: 20px;
        padding: 20px;
        border-left: 10px solid #10b981;
        margin: 20px 0;
        color: #064e3b;
    }

    /* 양옆 장식 (고정 위치) */
    .leaf-deco {
        position: fixed;
        bottom: -50px;
        left: -50px;
        width: 300px;
        opacity: 0.8;
        z-index: -1;
    }
    .leaf-deco-right {
        position: fixed;
        top: -50px;
        right: -50px;
        width: 350px;
        opacity: 0.7;
        transform: rotate(180deg);
        z-index: -1;
    }
    </style>
    
    <img src="https://www.pngarts.com/files/3/Green-Leaves-Transparent-Background-PNG.png" class="leaf-deco">
    <img src="https://www.pngarts.com/files/3/Green-Leaves-Transparent-Background-PNG.png" class="leaf-deco-right">
    """, unsafe_allow_html=True)

# --- [3. 메인 로직 및 점수 관리] ---
def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

# --- [4. 화면 레이아웃] ---
col1, col2, col3 = st.columns([1, 4, 1]) # 메인 콘텐츠 비율 조정

with col2:
    st.markdown("""
        <div class="header-text">
            <h1>🌿 Eco-Bot 챌린지</h1>
            <p>자연을 지키는 가장 까다로운 발걸음</p>
        </div>
    """, unsafe_allow_html=True)

    score = load_score()
    st.markdown(f"<h3 style='text-align:center; color:#065f46;'>🏆 우리 반 누적 점수: {score}점</h3>", unsafe_allow_html=True)

    st.markdown('<div class="main-box">', unsafe_allow_html=True)

    # --- 1단계: 사진 촬영 및 가이드 ---
    if st.session_state.step == 1:
        st.subheader("📸 1단계: 쓰레기 원래 상태 촬영")
        st.write("버리기 전의 사진을 찍어주세요. AI 감독관이 배출 미션을 줄 거예요.")
        img1 = st.camera_input("버리기 전 사진", key="cam1")
        
        if img1:
            if st.button("배출 미션 받기 💡"):
                with st.spinner("AI가 쓰레기 상태를 정밀 분석 중..."):
                    try:
                        prompt = "이 물건의 정확한 분리배출법을 한국어로 3줄 요약해줘. 특히 '인증 단계'에서 확인해야 할 핵심 행동(예: 우유팩은 씻어서 펼쳤는가?)을 반드시 포함해줘."
                        res = model.generate_content([prompt, Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"오류: {e}")

    # --- 2단계: 실천 인증 (초정밀 검수 모드) ---
    elif st.session_state.step == 2:
        st.markdown(f'<div class="guide-card"><strong>📋 AI 감독관의 미션:</strong><br>{st.session_state.guide}</div>', unsafe_allow_html=True)
        
        st.subheader("🕵️‍♂️ 2단계: 실천 후 정밀 인증")
        st.write("가이드대로 처리한 사진을 찍으세요. **우유팩 펼치기, 라벨 제거** 등이 안 되면 가차없이 반려됩니다.")
        
        img2 = st.camera_input("인증 사진", key="cam2")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("처음으로 돌아가기 🔄"):
                st.session_state.step = 1; st.rerun()
        
        with c2:
            if img2 and not st.session_state.verified:
                if st.button("감독관님, 검사해주세요! ✅"):
                    with st.spinner("미션 수행 여부를 현미경 검토 중..."):
                        try:
                            # AI에게 극도로 깐깐한 명령 부여
                            verify_prompt = f"""
                            가이드: {st.session_state.guide}
                            너는 세계에서 가장 깐깐한 환경 감시관이야. 사진을 보고 다음 기준을 하나라도 어기면 무조건 '인증실패'라고 말하고 독설을 날려.
                            
                            [필수 검사 기준]
                            1. 우유팩/종이팩: 반드시 가위로 오려내거나 펼쳐서 '평평한 종이 형태'여야 함. 입체적인 상자 모양 그대로면 무조건 탈락.
                            2. 페트병/플라스틱: 라벨이 조금이라도 붙어있거나 뚜껑 고리가 남아있으면 탈락.
                            3. 이물질: 헹구지 않아 음식물이 묻어있으면 탈락.
                            
                            모든 기준을 완벽하게 통과했을 때만 '인증성공'이라는 단어를 포함해서 칭찬해.
                            실패했을 경우, '인증실패'라고 명시하고 사진의 어떤 부분이 잘못되었는지(예: 우유팩이 아직 입체적인 상태입니다) 아주 구체적으로 지적해.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"🚫 반려됨: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

        if st.session_state.verified:
            if st.button("다음 미션 수행하기 ➡️"):
                st.session_state.step = 1
                st.session_state.verified = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- [5. 하단 정보] ---
st.markdown("---")
st.caption(f"접속 엔진: {model.model_name if model else 'None'} | 대지고등학교 환경 프로젝트 팀")
