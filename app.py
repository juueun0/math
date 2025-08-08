import streamlit as st
import pandas as pd
from st_gdrive import gdrive_connection

# --- Google Sheets 연결 설정 ---
# secrets.toml 파일에 있는 "gdrive" 연결 정보를 사용합니다.
# 자세한 설정 방법은 아래 설명을 참고해주세요.
try:
    conn = st.connection("gdrive", type="st-gdrive")
except Exception as e:
    st.error(f"Google Drive 연결에 실패했습니다. secrets.toml 파일 설정을 확인해주세요: {e}")
    st.stop()

# --- 페이지 설정 ---
st.set_page_config(
    page_title="2025학년도 개포고등학교 수학Ⅱ 성찰일지 확인표",
    page_icon="📝"
)

# --- 상태 관리 초기화 ---
# session_state를 사용하여 로그인 상태와 학생 데이터를 저장합니다.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_data = None

# --- 메인 제목 ---
st.title("2025학년도 개포고등학교 수학Ⅱ 성찰일지 확인표")
st.markdown("---")

# --- Google Sheet에서 데이터 불러오기 ---
# 여기에 자신의 Google Sheet URL 또는 ID를 입력하세요.
# 파일은 '전체 사용자(뷰어)' 권한으로 공유되어야 합니다.
GOOGLE_SHEET_URL = "여기에 구글 시트 URL 또는 ID를 입력하세요"
try:
    df = conn.read(url=GOOGLE_SHEET_URL, ttl=60) # 60초마다 데이터 새로고침
except Exception as e:
    st.error(f"Google 시트 데이터를 불러오는 데 실패했습니다. URL 또는 시트 권한을 확인해주세요: {e}")
    st.stop()

# 데이터프레임의 컬럼명을 사용하기 좋게 정리
df.columns = [col.replace(" ", "_") for col in df.columns]

# --- 로그인 화면 ---
if not st.session_state.logged_in:
    st.subheader("학번과 이름을 입력해주세요.")
    
    with st.form(key="login_form"):
        student_id = st.text_input("학번", placeholder="예: 20201")
        student_name = st.text_input("이름", placeholder="예: 김개포")
        submit_button = st.form_submit_button("확인")
        
    if submit_button:
        # 입력 값으로 데이터 필터링
        filtered_df = df[(df['학번'].astype(str) == student_id) & (df['이름'] == student_name)]
        
        if not filtered_df.empty:
            # 일치하는 데이터가 있으면 로그인 성공
            st.session_state.logged_in = True
            st.session_state.student_data = filtered_df.iloc[0]
            st.success("로그인 성공! 잠시 후 학생 정보를 표시합니다.")
            st.rerun()
        else:
            # 일치하는 데이터가 없으면 오류 메시지 표시
            st.error("학번과 이름이 올바르지 않습니다.")

# --- 학생 정보 화면 ---
else:
    st.subheader(f"안녕하세요, {st.session_state.student_data['이름']} 학생!")
    st.success("로그인에 성공했습니다.")
    st.markdown("---")
    
    st.write("### 학습지 제출 현황 및 점수")
    # 학생 데이터를 보기 좋게 DataFrame으로 보여줍니다.
    student_info = st.session_state.student_data.to_frame().T
    student_info.index = ['데이터']
    st.dataframe(student_info)

    # 로그아웃 버튼
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.student_data = None
        st.rerun()


