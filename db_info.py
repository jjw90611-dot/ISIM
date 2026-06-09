import streamlit as st
import sqlite3
import datetime
import random
import pandas as pd

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="산업안전지도사(기계) 면접 마스터", page_icon="⚙️", layout="wide")

# ==========================================
# [데이터베이스 설정] SQLite3 (학습 기록용)
# ==========================================
def init_db():
    conn = sqlite3.connect('safety_study.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS study_records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, 
                  category TEXT, 
                  question TEXT, 
                  user_answer TEXT, 
                  ai_feedback TEXT)''')
    conn.commit()
    return conn, c

conn, c = init_db()

# ==========================================
# [기출문제 데이터베이스] (제공된 문서 기반 샘플 추출)
# * 실제 운영 시 400문제를 모두 이 리스트에 추가하시면 됩니다.
# ==========================================
QUESTIONS = [
    {
        "category": "I. 산업안전관계법규",
        "question": "산업안전지도사의 직무에 대해 말해보세요.",
        "answer": "산업안전지도사란 산안법에 따라 사업장 내 근본적인 안전보건상의 문제점을 개선하는데 도움을 받고자 임명한 외부 전문가입니다.\n직무는 1. 공정상의 안전평가·지도 2. 유해위험 방지대책 평가·지도 3. 계획서와 보고서 작성 4. 위험성평가 지도 5. 안전보건개선계획서 작성 6. 자문에 대한 응답 및 조언입니다."
    },
    {
        "category": "I. 산업안전관계법규",
        "question": "위험성평가의 정의와 절차에 대해 말해보세요.",
        "answer": "위험성평가란 사업주가 스스로 사업장의 유해·위험요인을 파악하고 위험성 수준을 결정하여, 위험성을 낮추기 위한 적절한 조치를 마련하고 실행하는 과정입니다.\n절차는 1. 사전준비 2. 유해위험요인 파악 3. 위험성 결정 4. 위험성 감소대책 수립 및 실행 5. 위험성평가의 공유 6. 기록 및 보존 순으로 진행됩니다."
    },
    {
        "category": "I. 산업안전관계법규",
        "question": "안전난간의 구조와 설치조건에 대하여 설명해보세요.",
        "answer": "1. 상부난간대, 중간난간대, 발끝막이판 및 난간기둥으로 구성합니다.\n2. 상부난간대는 바닥면으로부터 90cm 이상 지점에 설치합니다.\n3. 발끝막이판은 바닥면으로부터 10cm 이상 높이를 유지합니다.\n4. 100kg 이상의 하중에 견딜 수 있는 튼튼한 구조여야 합니다."
    },
    {
        "category": "II. 기계안전기술",
        "question": "지게차의 위험성 및 안전대책에 대하여 설명해보세요.",
        "answer": "위험성은 화물의 낙하, 보행자와의 충돌/협착, 차량의 전도 위험이 있습니다.\n안전대책으로는 1. 작업계획서 작성 및 준수 2. 안전통로 확보(보행자 통로 구분) 3. 전조등, 후미등, 헤드가드 등 방호장치 설치 4. 전담관리자 지정 및 유자격자 운전 5. 제한속도 준수 및 유도자 배치가 있습니다."
    },
    {
        "category": "II. 기계안전기술",
        "question": "프레스 작업의 위험성과 대책(방호장치)에 대하여 설명해보세요.",
        "answer": "위험성은 기계 자체의 위험, 재료 송급/배출 시 신체 협착 위험 등이 있습니다.\n대책으로는 신체 일부가 위험 한계에 들어가지 않도록 덮개를 설치하거나, 방호장치를 설치해야 합니다.\n방호장치의 종류로는 손쳐내기식, 수인식, 양수조작식, 광전자식, 게이트가드식이 있습니다."
    },
    {
        "category": "III. 기계안전일반",
        "question": "페일 세이프(Fail Safe)와 풀 프루프(Fool Proof)의 차이점에 대해 설명하세요.",
        "answer": "풀 프루프는 인간의 실수(Human Error)를 방지하는 설계인 반면, 페일 세이프는 기계의 고장(Machine Failure)을 대비하는 설계의 안전구조입니다.\n즉, 에러의 원인이 기계 자체의 문제인지, 사람의 실수인지에 따라 구분됩니다."
    }
]

# ==========================================
# [사이드바 네비게이션]
# ==========================================
st.sidebar.title("⚙️ 기계안전 면접 마스터")
st.sidebar.markdown("---")
menu = st.sidebar.radio("메뉴를 선택하세요", 
    ["🏠 홈 (면접 가이드)", 
     "📚 주제별 핵심 문제", 
     "🎤 AI 실전 모의면접", 
     "🔍 면접 후기 & 트렌드", 
     "📝 내 학습 기록"]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** 면접은 10점 만점에 6점 이상이면 합격입니다. 두괄식으로 핵심 키워드를 먼저 말하는 연습을 하세요!")

# ==========================================
# 1. 홈 (면접 가이드)
# ==========================================
if menu == "🏠 홈 (면접 가이드)":
    st.title("🎯 산업안전지도사 3차 면접 가이드")
    st.markdown("제공된 서브노트를 바탕으로 정리된 **실전 면접 요령**입니다. 면접장 입실 전 반드시 숙지하세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("### 1. 답부터 말하자 (두괄식)")
        st.write("면접관은 채점을 위해 핵심 키워드(정답)를 기다리고 있습니다. 부연 설명부터 주저리주저리 읊조리면 좋은 점수를 받기 어렵습니다. **반드시 결론부터 먼저 제시**하고 부연 설명을 하세요.")
        
        st.warning("### 2. '3초'의 여유")
        st.write("질문이 끝나자마자 바로 답변하지 말고, **3초를 기다렸다 답변**하세요. 머릿속으로 구조화할 시간을 벌고, 면접관에게 신중한 이미지를 심어줄 수 있습니다.")
        
        st.info("### 3. 모르면 물어봐라")
        st.write("질문이 포괄적이어서 이해가 안 되면 지레짐작하지 말고 정중히 다시 물어보세요. 되물어본다고 감점을 주지 않습니다.")

    with col2:
        st.error("### 4. 주도권을 뺏기지 말자")
        st.write("단답형으로 끝내면 꼬리를 무는 압박 질문이 들어올 수 있습니다. 틈을 주지 않고 대화하듯이 자연스럽게 설명을 이어나가세요.")
        
        st.success("### 5. 가점 요인 (법적 근거)")
        st.write("법령 질문에 답할 때는 가급적 **법조문의 근거나 수치상의 표현**을 적용해 설득력을 높이세요. (예: '산업안전보건법 제36조에 근거하여~')")
        
        st.secondary("### 6. 인사는 곧 인성이다")
        st.write("입실할 때, 퇴실할 때 아주 정중하고 예의 바르게 인사하세요. 모르는 문제라도 끝까지 최선을 다하는 겸손한 자세가 중요합니다.")

# ==========================================
# 2. 주제별 핵심 문제
# ==========================================
elif menu == "📚 주제별 핵심 문제":
    st.title("📚 주제별 핵심 문제 학습")
    st.write("문서에 수록된 핵심 문제들을 카테고리별로 학습할 수 있습니다. 질문을 클릭하여 모범 답안을 확인하세요.")
    
    categories = list(set([q["category"] for q in QUESTIONS]))
    selected_category = st.selectbox("카테고리 선택", ["전체"] + categories)
    
    for idx, q in enumerate(QUESTIONS):
        if selected_category == "전체" or q["category"] == selected_category:
            with st.expander(f"Q. {q['question']}"):
                st.markdown(f"**[모범 답안]**\n\n{q['answer']}")

# ==========================================
# 3. AI 실전 모의면접
# ==========================================
elif menu == "🎤 AI 실전 모의면접":
    st.title("🎤 AI 실전 모의면접")
    st.write("실제 면접처럼 질문이 주어집니다. 소리 내어 답변해 본 후, 핵심 키워드를 텍스트로 입력하여 자가 진단해 보세요.")
    
    if 'current_q' not in st.session_state:
        st.session_state.current_q = random.choice(QUESTIONS)
        
    if st.button("🔄 새로운 문제 뽑기"):
        st.session_state.current_q = random.choice(QUESTIONS)
        
    st.markdown("---")
    st.subheader("🗣️ 면접관의 질문:")
    st.info(f"**{st.session_state.current_q['question']}**")
    
    user_answer = st.text_area("당신의 답변을 입력하세요 (핵심 키워드 위주로 작성):", height=150)
    
    if st.button("답변 제출 및 피드백 받기"):
        if user_answer:
            # 실제 서비스 시 여기에 Groq API 또는 OpenAI API 연동 코드를 삽입하여 피드백 생성
            # 예시용 가상 피드백 생성
            ai_feedback = "제출 완료! 아래 모범 답안과 본인의 답변을 비교하여 누락된 키워드가 없는지 확인하세요."
            
            # DB 저장
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO study_records (date, category, question, user_answer, ai_feedback) VALUES (?, ?, ?, ?, ?)",
                      (now, st.session_state.current_q['category'], st.session_state.current_q['question'], user_answer, ai_feedback))
            conn.commit()
            
            st.success("답변이 기록되었습니다!")
            st.markdown("### 💡 모범 답안 비교")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**[나의 답변]**")
                st.write(user_answer)
            with col2:
                st.markdown("**[모범 답안]**")
                st.write(st.session_state.current_q['answer'])
        else:
            st.warning("답변을 입력해주세요.")

# ==========================================
# 4. 면접 후기 & 트렌드 검색
# ==========================================
elif menu == "🔍 면접 후기 & 트렌드":
    st.title("🔍 실시간 면접 후기 및 트렌드 검색")
    st.write("산업안전지도사 기계안전 분야의 최신 3차 면접 후기와 기출 트렌드를 구글링하여 확인하세요.")
    
    # 큐레이션 된 유용한 링크 (실제 검색 결과 기반)
    st.subheader("📌 추천 면접 후기 링크 모음")
    st.markdown("""
    - [유튜브: 산업안전지도사 3차 면접 보고왔습니다!! 리얼 후기](https://www.youtube.com/watch?v=IF_A_KVQm-c)
    - [안전법인 한결: 3차 면접시험 세부 경험담 및 기출문제](https://www.hgsafety.co.kr/data/other)
    - [블로그: 산업안전지도사 3차 면접 기출문제 및 합격률 분석](https://anjenstory.tistory.com/65)
    """)
    
    st.markdown("---")
    st.subheader("🔎 직접 구글링하기")
    search_query = st.text_input("검색어를 입력하세요", value="산업안전지도사 기계안전 3차 면접 후기")
    
    if st.button("구글 검색 열기"):
        # Streamlit에서 새 창으로 구글 검색 결과를 띄우는 꼼수 (Markdown 활용)
        google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        st.markdown(f'<a href="{google_url}" target="_blank"><button style="background-color:#4285F4; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer;">🌐 구글에서 "{search_query}" 검색 결과 보기</button></a>', unsafe_allow_html=True)

# ==========================================
# 5. 내 학습 기록
# ==========================================
elif menu == "📝 내 학습 기록":
    st.title("📝 내 학습 기록")
    st.write("모의면접에서 작성했던 답변들을 복습하며 부족한 부분을 보완하세요.")
    
    df = pd.read_sql_query("SELECT date as '날짜', category as '카테고리', question as '질문', user_answer as '나의 답변' FROM study_records ORDER BY id DESC", conn)
    
    if df.empty:
        st.info("아직 학습 기록이 없습니다. 'AI 실전 모의면접'에서 답변을 제출해 보세요!")
    else:
        st.dataframe(df, use_container_width=True)
        
        # 기록 초기화 버튼
        if st.button("🗑️ 모든 기록 지우기"):
            c.execute("DELETE FROM study_records")
            conn.commit()
            st.success("기록이 초기화되었습니다. 새로고침(F5)을 눌러주세요.")

