import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

# --- [1. 기본 설정 및 AI 연결] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="♻️", layout="wide")

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

# --- [2. 화려한 에코 테마 CSS 및 캐릭터 설정] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    
    /* 배경: 은은한 파스텔톤 그린 그라데이션과 패턴 */
    .stApp {
        background: #f0fdf4;
        background-image: 
            radial-gradient(at 0% 0%, rgba(167, 243, 208, 0.5) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(187, 247, 208, 0.5) 0px, transparent 50%),
            url("https://www.transparenttextures.com/patterns/leaf.png");
        font-family: 'Pretendard', sans-serif;
    }

    /* 메인 컨텐츠 카드: 가독성을 위해 불투명도 높임 */
    .main-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 30px;
        padding: 40px;
        border: 2px solid #10b981;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        margin: 20px auto;
        max-width: 850px;
        color: #1f2937;
    }

    /* 마스코트 '에코루' 말풍선 스타일 */
    .mascot-talk {
        background: #DCFCE7;
        padding: 15px 20px;
        border-radius: 20px;
        border-bottom-left-radius: 2px;
        margin-bottom: 20px;
        border: 1px solid #10b981;
        color: #064e3b;
        font-weight: 700;
        position: relative;
    }

    /* 타이틀 디자인 */
    .header-text h1 { 
        font-size: 3.2rem; 
        font-weight: 800; 
        color: #065f46; 
        text-align: center;
        margin-bottom: 5px;
    }
    .header-text p { 
        text-align: center;
        color: #059669; 
        font-size: 1.2rem;
        margin-bottom: 30px;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background: #10b981 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px 25px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* 아이콘 애니메이션 */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    .floating-icon {
        font-size: 3rem;
        animation: float 4s ease-in-out infinite;
        position: fixed;
        z-index: -1;
        opacity: 0.3;
    }
    </style>
    
    <!-- 움직이는 배경 아이콘들 -->
    <div class="floating-icon" style="top: 15%; left: 5%;">🌿</div>
    <div class="floating-icon" style="top: 60%; left: 8%;">♻️</div>
    <div class="floating-icon" style="top: 20%; right: 7%;">🌍</div>
    <div class="floating-icon" style="top: 70%; right: 10%;">🌳</div>
    <div class="floating-icon" style="top: 40%; left: 2%;">✨</div>
    """, unsafe_allow_html=True)

# --- [3. 점수 관리 기능] ---
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

# --- [4. 레이아웃: 양옆 마스코트 배치] ---
col_side_1, col_center, col_side_2 = st.columns([1, 2.5, 1])

# 왼쪽 마스코트 영역
with col_side_1:
    st.write("") # 간격
    st.image("https://cdn-icons-png.flaticon.com/512/2544/2544111.png", caption="Eco-Buddy 에코루", use_column_width=True)
    st.markdown("""
        <div class="mascot-talk">
            "내 이름은 에코루! 지구를 지키는 학생 로봇이야. 분리배출 똑바로 안 하면 혼낼거야!"
        </div>
    """, unsafe_allow_html=True)

# 오른쪽 마스코트 영역 (정보 표시)
with col_side_2:
    st.write("")
    st.image("https://cdn-icons-png.flaticon.com/512/3074/3074058.png", use_column_width=True)
    st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 20px; border: 2px solid #10b981; text-align: center;">
            <h4 style="margin:0; color:#065f46;">🏆 누적 점수</h4>
            <h1 style="margin:0; color:#10b981;">{load_score()}</h1>
        </div>
    """, unsafe_allow_html=True)

# 중앙 메인 컨텐츠 영역
with col_center:
    st.markdown("""
        <div class="header-text">
            <h1>♻️ Eco-Bot 챌린지</h1>
            <p>에코루와 함께하는 똑똑한 분리배출 인증</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # --- 1단계: 미션 생성 ---
    if st.session_state.step == 1:
        st.markdown("### 📸 1단계: 버리기 전 사진 찍기")
        st.write("버릴 물건을 에코루에게 보여주세요. 어떻게 정리해야 할지 알려줄게요!")
        img1 = st.camera_input("카메라 실행", key="cam1")
        
        if img1:
            if st.button("에코루에게 배출법 물어보기 💡"):
                with st.spinner("에코루가 분석 중..."):
                    try:
                        prompt = "이 물건의 분리배출법을 한국어로 친절하지만 깐깐하게 알려줘. 특히 씻기, 라벨 떼기, 펼치기 등의 행동을 강조해줘."
                        res = model.generate_content([prompt, Image.open(img1)])
                        st.session_state.guide = res.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e: st.error(f"에러가 났어! 다시 해줘: {e}")

    # --- 2단계: 깐깐한 인증 ---
    elif st.session_state.step == 2:
        st.markdown(f"""
            <div style="background:#f0fdf4; padding:20px; border-radius:15px; border-left:8px solid #10b981; margin-bottom:20px;">
                <h4 style="margin-top:0; color:#064e3b;">📝 에코루의 미션 가이드</h4>
                <p style="color:#166534;">{st.session_state.guide}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🕵️‍♂️ 2단계: 완벽 인증샷 찍기")
        st.write("**주의:** 우유팩은 쫙 펼쳐야 하고, 라벨은 흔적도 없어야 성공이야!")
        
        img2 = st.camera_input("인증샷 촬영", key="cam2")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("처음부터 다시 할래 🔄"):
                st.session_state.step = 1; st.rerun()
        
        with btn_col2:
            if img2 and not st.session_state.verified:
                if st.button("에코루, 검토해줘! ✅"):
                    with st.spinner("현미경으로 검사 중..."):
                        try:
                            verify_prompt = f"""
                            이전 가이드: {st.session_state.guide}
                            너는 이제부터 분리배출 검사 전문가 '에코루'야.
                            [검사 기준]
                            1. 우유팩/종이 상자: 무조건 '평평하게 펼쳐진' 상태여야 함. 입체적이면 가차없이 탈락.
                            2. 페트병: 라벨이 단 1%라도 남아있으면 탈락.
                            3. 이물질: 붉은 양념이나 찌꺼기가 보이면 탈락.
                            
                            조건을 모두 충족하면 '인증성공'이라 말하고 칭찬해줘.
                            기준에 미달하면 '인증실패'라 말하고 무엇이 잘못되었는지 학생에게 꾸짖듯이 말해줘.
                            """
                            res = model.generate_content([verify_prompt, Image.open(img2)])
                            
                            if "인증성공" in res.text:
                                add_score()
                                st.session_state.verified = True
                                st.balloons()
                                st.success(res.text)
                            else:
                                st.error(f"❌ 에코루의 판정: {res.text}")
                        except Exception as e: st.error(f"오류: {e}")

        if st.session_state.verified:
            if st.button("다음 쓰레기 하러 가기 ➡️"):
                st.session_state.step = 1
                st.session_state.verified = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- [5. 하단 정보] ---
st.markdown("---")
st.caption("🌱 대지고등학교 환경 프로젝트 팀 | AI 마스코트 에코루 가동 중")
