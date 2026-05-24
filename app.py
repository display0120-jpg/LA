import streamlit as st
from groq import Groq
from PIL import Image
import os
import base64
import io

# --- [1. API 클라이언트 설정 (Secrets 사용)] ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("설정 오류: Streamlit Cloud의 Secrets에 'GROQ_API_KEY'를 등록해주세요.")
    st.stop()

# --- [2. 브랜딩 & 디자인 세팅] ---
st.set_page_config(page_title="Eco-Bot 챌린지", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; font-size: 16px; }
    .stApp { background-color: #ECFDF5; } 
    .header-container {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        padding: 30px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bot-card {
        background-color: white; padding: 20px; border-radius: 20px;
        border: 2px solid #A7F3D0; margin-bottom: 15px;
        display: flex; align-items: center; gap: 15px; color: #1F2937;
    }
    .mission-card {
        background-color: #F0FDF4; padding: 15px; border-radius: 15px;
        border-left: 8px solid #059669; margin: 10px 0; color: #111827;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%; border-radius: 15px !important;
        background-color: #059669 !important; color: white !important;
        font-weight: 700 !important; height: 3.5em !important; border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [3. 유틸리티 함수] ---
def encode_image(image_file):
    """이미지 객체를 Base64로 변환하여 Groq API에 전달 가능한 형식으로 만듦"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def call_groq_vision(prompt, base64_image):
    """Groq Llama 3.2 Vision 모델 호출"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            temperature=0.1, # 일관된 답변을 위해 낮게 설정
            max_tokens=512,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {e}"

def load_score():
    if not os.path.exists("eco_score.txt"): return 0
    with open("eco_score.txt", "r") as f: 
        try: return int(f.read())
        except: return 0

def add_score():
    score = load_score() + 1
    with open("eco_score.txt", "w") as f: f.write(str(score))
    return score

# --- [4. 앱 상태 관리] ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'guide' not in st.session_state: st.session_state.guide = ""
if 'verified' not in st.session_state: st.session_state.verified = False

def reset_app():
    st.session_state.step = 1
    st.session_state.guide = ""
    st.session_state.verified = False
    st.rerun()

# --- [5. 메인 UI 화면 구성] ---
st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 26px;">🤖 Eco-Bot 챌린지</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">Groq AI 기반 분리배출 인증</p>
    </div>
    """, unsafe_allow_html=True)

score = load_score()
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#065F46; margin-bottom:15px;'>현재 우리 반 누적 점수: {score}점 🏆</div>", unsafe_allow_html=True)

# [1단계: 쓰레기 인식 및 가이드 제공]
if st.session_state.step == 1:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🤖</div>
            <div>
                <strong>안녕! 난 에코봇이야.</strong><br>
                쓰레기 사진을 찍으면 어떻게 버리는지 알려줄게!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    img1 = st.camera_input("1단계: 버리기 전 사진 촬영", key="cam1")
    
    if img1:
        if st.button("분리배출 가이드 보기 💡"):
            with st.spinner("AI가 분석 중..."):
                base64_img = encode_image(img1)
                prompt = "이 쓰레기를 어떻게 분리배출해야 하는지 한국어로 아주 짧게 딱 3줄로 알려줘. 1.비움, 2.제거, 3.분류 형식으로!"
                res_text = call_groq_vision(prompt, base64_img)
                st.session_state.guide = res_text
                st.session_state.step = 2
                st.rerun()

# [2단계: 실천 인증]
elif st.session_state.step == 2:
    st.markdown("""
        <div class="bot-card">
            <div style="font-size:40px;">🕵️‍♂️</div>
            <div>
                <strong>가이드대로 실천했니?</strong><br>
                깨끗해진 모습을 다시 찍어서 인증해줘!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='mission-card'><strong>📝 배출 가이드:</strong><br>{st.session_state.guide}</div>", unsafe_allow_html=True)
    
    img2 = st.camera_input("2단계: 실천 후 사진 촬영", key="cam2")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("처음부터 다시하기 🔄"): reset_app()

    if img2 and not st.session_state.verified:
        with col2:
            if st.button("최종 인증 완료 ✅"):
                with st.spinner("검수 중..."):
                    base64_img2 = encode_image(img2)
                    verify_prompt = f"사용자 가이드: {st.session_state.guide}. 사진을 보고 가이드대로 잘 했는지 확인해줘. 성공했다면 무조건 '인증성공'이라는 단어를 포함해서 한 줄로 칭찬해주고, 아니면 부족한 점을 딱 한 줄만 말해줘."
                    res_text = call_groq_vision(verify_prompt, base64_img2)
                    
                    if "인증성공" in res_text or "성공" in res_text:
                        add_score()
                        st.session_state.verified = True
                        st.balloons()
                        st.success(res_text)
                    else:
                        st.error(res_text)

    if st.session_state.verified:
        if st.button("다음 쓰레기 인증하기 ➡️"): reset_app()

st.markdown("---")
st.caption("대지고등학교 환경 프로젝트 | 모델: Llama-3.2-11b-Vision")
