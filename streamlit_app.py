import streamlit as st
# set_page_config()는 항상 다른 Streamlit 명령어보다 먼저 와야 합니다
st.set_page_config(page_title="SQL 학습 도우미", layout="wide")

import openai
import datetime
import traceback
import html

st.title("🔍 SQL 단계별 학습 도우미")

# OpenAI API 키 입력 받기
st.sidebar.subheader("🔐 OpenAI API Key 설정")
api_key = st.sidebar.text_input("API Key를 입력하세요", type="password")
if not api_key:
    st.warning("OpenAI API 키를 입력해주세요.")
    st.stop()
openai.api_key = api_key

# 학습 단계 정의
if 'learning_paths' not in st.session_state:
    st.session_state.learning_paths = {
        "초급": [
            "SQL 기본 개념 이해하기",
            "SELECT 문 기초",
            "WHERE 절과 필터링",
            "ORDER BY와 정렬",
            "INSERT, UPDATE, DELETE 기본 명령어",
            "기본 데이터 타입",
            "테이블 생성 및 수정 기초"
        ],
        "중급": [
            "JOIN 구문 마스터하기",
            "서브쿼리 활용",
            "집계 함수와 GROUP BY",
            "HAVING 절",
            "인덱스 이해와 활용",
            "뷰(VIEW) 생성 및 활용",
            "트랜잭션 이해하기"
        ],
        "고급": [
            "저장 프로시저와 함수",
            "트리거 활용",
            "성능 최적화 기법",
            "실행 계획 분석",
            "고급 인덱싱 전략",
            "파티셔닝",
            "SQL 보안 관리"
        ],
        "특화": [
            "데이터 모델링 기법",
            "데이터 웨어하우스 설계",
            "ETL 프로세스",
            "대용량 데이터 처리 기법",
            "NoSQL과 SQL 통합 전략",
            "클라우드 데이터베이스 활용",
            "SQL과 BI 도구 연동"
        ]
    }

# 템플릿 정의 - 학습자 친화형 개념 설명 템플릿 적용
if 'templates' not in st.session_state:
    st.session_state.templates = {
        "개념 설명": '''
다음 SQL 주제에 대해 **초보자도 쉽게 이해할 수 있게** 학습 자료를 작성해줘:

- 주제: {topic}
- 학습 단계: {level}

다음 형식으로 Markdown으로 작성해줘:

1. 개념 설명 (초등학생도 이해할 수 있게 쉬운 비유 포함)
2. 왜 중요한지 알려줘 (현업 예시 포함)
3. 실제 데이터 예시를 만들어서 테이블과 함께 설명해줘
4. SQL 문법 예시 (한 줄씩 해설 추가)
5. 실습 과정을 단계별로 안내해줘 (예: 1단계: 테이블 생성, 2단계: 쿼리 작성)
6. 따라 하면서 결과를 직접 확인할 수 있도록 결과 예시도 보여줘
7. 주의해야 할 실수나 자주 틀리는 부분
8. 다음 단계 추천 학습
9. 연습 문제 (쉬움~어려움 순서로 3문제)
10. 추천 자료 링크 (유튜브, 블로그 등 실제 존재하는 자료 위주)

※ 모든 SQL 예제는 실행 가능한 상태로 작성해줘  
※ 설명은 꼭 '말로 대화하듯' 친근하게 해줘  
※ 가능한 경우, 표/그림/결과 예시도 마크다운으로 표현해줘
        ''',
        "문제 해결": """SQL {topic}와 관련된 일반적인 문제 상황과 해결 방법을 {level} 수준에 맞게 작성해주세요.
        최소 3개의 문제 시나리오와 각각의 해결책을 SQL 코드와 함께 제시해주세요.
        문제 해결 과정의 설명과 코드 실행 결과도 포함해주세요.""",
        
        "실무 예제": """SQL {topic}을 실무에서 활용할 수 있는 구체적인 예제를 {level} 수준에 맞게 작성해주세요.
        업무 상황 설명, 요구사항 분석, SQL 코드 작성, 결과 해석 순으로 작성해주세요.
        실제 비즈니스 시나리오에 적용할 수 있는 최소 2개의 사례를 제공해주세요.""",
        
        "데이터베이스 최적화": """SQL {topic}을 통한 데이터베이스 성능 최적화 방법을 {level} 수준에 맞게 작성해주세요.
        성능 이슈의 원인 분석, 최적화 전략, 코드 개선 예시를 포함해주세요.
        최적화 전/후 성능 비교와 실제 적용 시 주의사항도 설명해주세요."""
    }

# 학습 이력 관리
if 'history' not in st.session_state:
    st.session_state.history = []

# 사용자 진행 상황
if 'user_progress' not in st.session_state:
    st.session_state.user_progress = {
        "current_level": "초급",
        "completed_topics": []
    }

# 주차별 교육 계획
if 'weekly_plan' not in st.session_state:
    st.session_state.weekly_plan = {
        "1주차": ["SQL 기본 개념 이해하기", "SELECT 문 기초", "WHERE 절과 필터링"],
        "2주차": ["ORDER BY와 정렬", "INSERT, UPDATE, DELETE 기본 명령어", "기본 데이터 타입"],
        "3주차": ["JOIN 구문 마스터하기", "서브쿼리 활용", "집계 함수와 GROUP BY"],
        "4주차": ["VIEW 생성 및 활용", "트랜잭션 이해하기", "저장 프로시저와 함수"]
    }

# 자동화 설정
if 'automation_settings' not in st.session_state:
    st.session_state.automation_settings = {
        "enabled": False,
        "schedule": "매주 월요일",
        "target_emails": [],
        "template": "개념 설명",
        "current_week": 1,
        "subject_template": "[SQL 학습] {topic} 학습 자료",
        "email_template": "안녕하세요,\n\n이번 주 SQL 학습 주제인 '{topic}'에 대한 학습 자료를 공유드립니다."
    }

# 탭 생성
tabs = st.tabs(["📚 학습 자료", "📊 진행 현황", "📧 자료 자동화"])

# 첫 번째 탭: 학습 자료
with tabs[0]:
    st.header("📚 SQL 학습 자료 생성")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🎯 {st.session_state.user_progress['current_level']} 학습 주제")
        topic_options = st.session_state.learning_paths[st.session_state.user_progress["current_level"]]
        selected_topic = st.selectbox("학습할 주제를 선택하세요", topic_options, key="topic_select")
        
        template_options = list(st.session_state.templates.keys())
        selected_template = st.selectbox("학습 유형 선택", template_options, key="template_select")
        custom_request = st.text_area("추가 질문이나 특별 요청이 있으면 입력하세요 (선택사항)", height=100, key="custom_request")

    with col2:
        st.subheader("📊 학습 현황")
        st.write(f"현재 단계: {st.session_state.user_progress['current_level']}")
        
        st.subheader("📚 학습 경로")
        current_level_topics = st.session_state.learning_paths[st.session_state.user_progress["current_level"]]
        for topic in current_level_topics:
            is_completed = topic in st.session_state.user_progress["completed_topics"]
            st.markdown(f"{'✅' if is_completed else '⬜'} {topic}")
        
        st.subheader("🔄 학습 단계 변경")
        new_level = st.selectbox(
            "학습 단계 선택", 
            list(st.session_state.learning_paths.keys()),
            index=list(st.session_state.learning_paths.keys()).index(st.session_state.user_progress["current_level"]),
            key="level_change"
        )
        if st.button("단계 변경", key="change_level_btn"):
            st.session_state.user_progress["current_level"] = new_level
            st.rerun()
        
        st.subheader("⚙️ 설정")
        model_options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        selected_model = st.selectbox("OpenAI 모델 선택", model_options, key="model_select")

    col1, col2 = st.columns([1, 3])
    with col1:
        generate_button = st.button("📚 학습 자료 생성", type="primary", use_container_width=True)
    with col2:
        if st.button("✅ 주제 완료 표시", use_container_width=True):
            if selected_topic not in st.session_state.user_progress["completed_topics"]:
                st.session_state.user_progress["completed_topics"].append(selected_topic)
                st.success(f"'{selected_topic}' 주제를 완료했습니다!")
                st.experimental_rerun()

    def save_result(topic, level, content, template_name):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "topic": topic,
            "level": level,
            "template": template_name,
            "content": content
        }
        st.session_state.history.append(result)
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]

    # 마크다운을 직접 HTML 텍스트에 포함
    def create_html_with_markdown(markdown_content, title):
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title} - SQL 학습 자료</title>
    <style>
        body {{ font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif; padding: 20px; line-height: 1.6; }}
        h1, h2, h3, h4, h5, h6 {{ color: #333; margin-top: 20px; font-weight: bold; font-size: 12pt; }}
        p, li, td, th {{ font-size: 10pt; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 10pt; }}
        code {{ font-family: Consolas, monospace; font-size: 10pt; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .markdown-content {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="markdown-content">
{markdown_content}
    </div>
</body>
</html>"""
        return html_content

    # 학습 자료 생성 시 실행
    if generate_button:
        with st.spinner(f"'{selected_topic}' 학습 자료를 생성 중입니다..."):
            try:
                template = st.session_state.templates[selected_template]
                formatted_prompt = template.format(topic=selected_topic, level=st.session_state.user_progress["current_level"])
                if custom_request:
                    formatted_prompt += f"\n\n추가 요청사항: {custom_request}"

                response = openai.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "당신은 SQL 전문 튜터입니다. 학습자의 수준에 맞춰 정확하고 실용적인 SQL 학습 자료를 Markdown 형식으로 작성하세요. 모든 SQL 예제는 실제 실행 가능해야 합니다."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                save_result(selected_topic, st.session_state.user_progress["current_level"], content, selected_template)

                # 세션 상태에 생성된 내용 저장
                st.session_state.generated_content = content
                st.session_state.generated_html = create_html_with_markdown(content, selected_topic)
                st.session_state.generated_topic = selected_topic
                
                st.success(f"'{selected_topic}' 학습 자료가 생성되었습니다.")
                st.subheader("📖 학습 자료 (Markdown)")
                st.markdown(content)
                
                # 고유 타임스탬프 생성
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                md_filename = f"SQL_{selected_topic.replace(' ', '_')}_{timestamp}.md"
                
                # 세 개의 다운로드 버튼을 나란히 배치
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Markdown 다운로드 버튼
                    st.download_button(
                        "📥 Markdown 파일로 다운로드", 
                        data=content, 
                        file_name=md_filename, 
                        mime="text/markdown",
                        key=f"download_md_{timestamp}"
                    )
                
                html_content = st.session_state.generated_html
                html_filename = f"SQL_{selected_topic.replace(' ', '_')}_{timestamp}.html"
                
                with col2:
                    # HTML 다운로드 버튼
                    st.download_button(
                        "📥 HTML 파일로 다운로드", 
                        data=html_content, 
                        file_name=html_filename, 
                        mime="text/html",
                        key=f"download_html_{timestamp}"
                    )
                
                # 화면 그대로 캡처하는 HTML 생성
                with col3:
                    # 화면 캡처 HTML 생성
                    screen_capture_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{selected_topic} - SQL 학습 자료 (화면 그대로)</title>
    <style>
        body {{ font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif; padding: 20px; line-height: 1.6; background-color: #f9f9f9; }}
        .content-box {{ background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #1E88E5; font-size: 24px; margin-bottom: 20px; text-align: center; }}
        h2 {{ color: #333; font-size: 16px; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
        h3, h4, h5, h6 {{ color: #333; font-size: 12pt; font-weight: bold; }}
        p, li {{ font-size: 10pt; line-height: 1.6; }}
        pre {{ background-color: #f5f5f5; padding: 12px; border-radius: 5px; overflow-x: auto; border: 1px solid #eee; }}
        code {{ font-family: Consolas, monospace; font-size: 10pt; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 10pt; }}
        th {{ background-color: #f2f2f2; }}
        .header {{ background-color: #1E88E5; color: white; padding: 15px; border-radius: 10px 10px 0 0; margin-bottom: 20px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 10pt; }}
        .success-message {{ background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SQL 학습 도우미 - {selected_topic}</h1>
    </div>
    <div class="content-box">
        <div class="success-message">'{selected_topic}' 학습 자료가 생성되었습니다.</div>
        <h2>📖 학습 자료</h2>
        <div class="markdown-content">
{content.replace('```', '<pre><code>').replace('```', '</code></pre>')}
        </div>
    </div>
    <div class="footer">
        © 2025 SQL 단계별 학습 도우미 | 생성 시간: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>"""
                    
                    screen_capture_filename = f"SQL_{selected_topic.replace(' ', '_')}_화면캡처_{timestamp}.html"
                    
                    # 화면 캡처 다운로드 버튼
                    st.download_button(
                        "📥 화면 그대로 저장하기", 
                        data=screen_capture_html, 
                        file_name=screen_capture_filename, 
                        mime="text/html",
                        key=f"download_screen_{timestamp}"
                    )
                
                with st.expander("🔽 Confluence용 HTML 보기/복사"):
                    st.code(html_content, language="html")
                
            except Exception as e:
                st.error("학습 자료 생성 중 오류가 발생했습니다.")
                st.error(f"오류 메시지: {str(e)}")
                st.code(traceback.format_exc())

                content = response.choices[0].message.content
                save_result(selected_topic, st.session_state.user_progress["current_level"], content, selected_template)

                # 세션 상태에 생성된 내용 저장
                st.session_state.generated_content = content
                st.session_state.generated_html = create_html_with_markdown(content, selected_topic)
                st.session_state.generated_topic = selected_topic
                
                st.success(f"'{selected_topic}' 학습 자료가 생성되었습니다.")
                st.subheader("📖 학습 자료 (Markdown)")
                st.markdown(content)
                
                # 고유 타임스탬프 생성
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                md_filename = f"SQL_{selected_topic.replace(' ', '_')}_{timestamp}.md"
                
                # 다운로드 버튼
                st.download_button(
                    "📥 Markdown 파일로 다운로드", 
                    data=content, 
                    file_name=md_filename, 
                    mime="text/markdown",
                    key=f"download_md_{timestamp}"
                )
                
                html_content = st.session_state.generated_html
                html_filename = f"SQL_{selected_topic.replace(' ', '_')}_{timestamp}.html"
                
                with st.expander("🔽 Confluence용 HTML 보기/복사"):
                    st.code(html_content, language="html")
                
                st.download_button(
                    "📥 HTML 파일로 다운로드 (Confluence용)", 
                    data=html_content, 
                    file_name=html_filename, 
                    mime="text/html",
                    key=f"download_html_{timestamp}"
                )

    # 이제 필요 없는 코드이므로 제거

            except Exception as e:
                st.error("학습 자료 생성 중 오류가 발생했습니다.")
                st.error(f"오류 메시지: {str(e)}")
                st.code(traceback.format_exc())

# 두 번째 탭: 진행 현황
with tabs[1]:
    st.header("📊 진행 현황")
    
    st.subheader("🎯 주제별 완료 현황")
    all_topics = []
    for level, topics in st.session_state.learning_paths.items():
        all_topics.extend(topics)
    
    completed_count = len(st.session_state.user_progress["completed_topics"])
    total_count = len(all_topics)
    
    progress_percentage = completed_count / total_count if total_count > 0 else 0
    st.write(f"전체 진행률: {completed_count}/{total_count} 주제 완료 ({progress_percentage:.1%})")
    st.progress(progress_percentage)
    
    st.subheader("📅 주차별 교육 계획")
    for week, topics in st.session_state.weekly_plan.items():
        with st.expander(f"{week}"):
            for topic in topics:
                completed = topic in st.session_state.user_progress["completed_topics"]
                st.markdown(f"{'✅' if completed else '⬜'} {topic}")

    st.subheader("📊 주차별 진도 현황 요약")
    for week, topics in st.session_state.weekly_plan.items():
        completed = [t for t in topics if t in st.session_state.user_progress["completed_topics"]]
        progress = len(completed) / len(topics) if len(topics) > 0 else 0
        st.write(f"{week} - 완료: {len(completed)} / {len(topics)}")
        st.progress(progress)
    
    st.subheader("📜 학습 자료 이력")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.expander(f"{item['timestamp']} - {item['topic']} ({item['template']})"):
                st.markdown(item['content'])
    else:
        st.info("아직 생성된 학습 자료가 없습니다.")

# 세 번째 탭: 자료 자동화
with tabs[2]:
    st.header("📧 자료 자동화")
    
    st.subheader("🔄 자동 자료 생성 및 배포 설정")
    
    auto_enabled = st.checkbox("자동화 활성화", value=st.session_state.automation_settings["enabled"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        schedule_options = ["매일", "매주 월요일", "매주 수요일", "매주 금요일", "매월 1일"]
        auto_schedule = st.selectbox(
            "일정", 
            schedule_options,
            index=schedule_options.index(st.session_state.automation_settings["schedule"]) if st.session_state.automation_settings["schedule"] in schedule_options else 0
        )
        
        auto_week = st.number_input(
            "현재 주차 설정", 
            min_value=1, 
            max_value=4, 
            value=st.session_state.automation_settings["current_week"]
        )
        
        auto_template = st.selectbox(
            "템플릿", 
            list(st.session_state.templates.keys()),
            index=list(st.session_state.templates.keys()).index(st.session_state.automation_settings["template"]) if st.session_state.automation_settings["template"] in st.session_state.templates else 0
        )
    
    with col2:
        auto_emails = st.text_area(
            "대상 이메일 (줄바꿈으로 구분)", 
            "\n".join(st.session_state.automation_settings["target_emails"])
        )
        
        auto_subject = st.text_input(
            "이메일 제목 템플릿", 
            value=st.session_state.automation_settings["subject_template"]
        )
        
        auto_body = st.text_area(
            "이메일 본문 템플릿", 
            value=st.session_state.automation_settings["email_template"],
            height=100
        )
    
    if st.button("자동화 설정 저장", type="primary"):
        st.session_state.automation_settings = {
            "enabled": auto_enabled,
            "schedule": auto_schedule,
            "target_emails": [email.strip() for email in auto_emails.split("\n") if email.strip()],
            "template": auto_template,
            "current_week": auto_week,
            "subject_template": auto_subject,
            "email_template": auto_body
        }
        st.success("자동화 설정이 저장되었습니다!")
    
    st.subheader("📆 일정 미리보기")
    
    # 현재 주차에 해당하는 주제들 가져오기
    current_week_key = f"{auto_week}주차"
    current_week_topics = st.session_state.weekly_plan.get(current_week_key, [])
    
    st.write(f"현재 설정된 주차: **{current_week_key}**")
    
    if current_week_topics:
        st.write("이번 주에 자동 생성될 주제:")
        for i, topic in enumerate(current_week_topics):
            st.write(f"{i+1}. {topic}")
        
        st.info(f"위 주제들은 {auto_schedule}에 선택된 이메일로 자동 발송됩니다.")
    else:
        st.warning(f"{current_week_key}에 해당하는 주제가 없습니다.")
    
    # 미리보기 생성
    if st.button("다음 발송 미리보기"):
        if not current_week_topics:
            st.error("현재 주차에 해당하는 주제가 없습니다.")
        else:
            next_topic = current_week_topics[0]  # 예시로 첫 번째 주제 선택
            
            next_subject = auto_subject.format(topic=next_topic)
            next_body = auto_body.format(topic=next_topic)
            
            st.subheader("다음 발송 미리보기")
            st.code(f"제목: {next_subject}\n\n{next_body}")
            
            st.write(f"대상: {len(st.session_state.automation_settings['target_emails'])}명")
            for email in st.session_state.automation_settings["target_emails"]:
                st.write(f"- {email}")

# 푸터
st.divider()
st.caption("© 2025 SQL 단계별 학습 도우미 | SQL 실력 향상을 위한 맞춤형 학습 플랫폼")