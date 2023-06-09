import openai
import PyPDF2
import streamlit as st
import pandas as pd
import time


openai.api_key = st.secrets["api_secret"]

st.title('Assurance DA')
st.header('AI Consultant - 계약서검토')
st.markdown("<div style='text-align: right;'>Developed by Assurance DA (문의 : <a href = \"mailto:jae-dong.kim@pwc.com\">jae-dong.kim@pwc.com</a>)</div>", unsafe_allow_html=True)
st.write("")
st.markdown("<br>", unsafe_allow_html=True)

st.write('계약서를 업로드하고 무엇이든 물어보세요!')

pdf_file = None
txt_file = None
pdf_file = st.file_uploader("파일을 선택하세요(PDF만 가능)", type=['pdf'])
# txt_file = st.file_uploader("파일을 선택하세요(TXT만 가능)", type=['txt'])
csv_file = st.file_uploader("질문 파일을 선택하세요(csv만 가능 1열 제목, 2열 질문)", type=['csv'])

dataframe = None

conversation = []
conversation.append(
    {
        'role': 'system',
        'content': '다음 계약서를 읽고 묻는 질문에 답변을 기재하고 답변을 찾을 수 있는 조항을 문장 마지막에 괄호안에 알려줘: '
    }
)

def chatGPT_conversation(conversation_input):
    response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=conversation_input
    )

    return response

# file_name = '게임 (도급) 표준계약서.pdf'


def ask_question(conversation, content):
    conversation_try = conversation.copy()
    conversation_try.append(
        {
            "role": "user",
            "content": content
        }
    )
    print(conversation_try)
    answer = chatGPT_conversation(conversation_try)
    print(answer)
    print('-*'*50)
    answer_content = answer.choices[0].message.content

    return answer_content


def convert_df(df):
   return df.to_csv(index=False).encode('cp949')


if txt_file is not None or pdf_file is not None:

    if pdf_file is not None:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        n = 0
        page_obj = []
        for page in range(len(pdf_reader.pages)):
            n += 1
            page_obj.append(pdf_reader.pages[page].extract_text())

        data = '\n'.join(page_obj)
        file_name = pdf_file.name

    elif txt_file is not None:

        file = txt_file.read()
        data = file.decode('utf-8')
        file_name = txt_file.name

    if csv_file is not None:

        dataframe = pd.read_csv(csv_file)
        st.subheader('기본 질문 리스트')
        st.write(dataframe)

        conversation.append({"role": "system", "content": data})

        result_dataframe = dataframe.copy()
        result_dataframe['결과'] = ''

    # 사용자의 입력이 있는 경우
    if st.button('기본 질문 제출'):

        if data is not None and dataframe is not None:

            for i, row in dataframe.iterrows():
                row_title = row[0]
                row_question = row[1]

                st.subheader(row_title)
                row_answer = ask_question(conversation, row_question)
                result_dataframe.loc[i, '결과'] = row_answer

                st.write(row_answer)

            st.download_button(
                "결과 파일 다운로드",
                convert_df(result_dataframe),
                f"ChatGPT_{file_name}.csv",
                "text/csv",
                key='download-csv'
                )

        else:

            st.info('계약서 PDF 와 질문 리스트를 업로드 해주세요')

    user_msg = st.text_input('계약서에 대하여 추가로 무엇이 궁금하신가요?')

    if st.button('추가 질문 제출'):
        # 사용자의 입력 받기

        if data is not None and dataframe is not None:

            conversation.append(
                {
                    "role": "user",
                    "content": user_msg
                }
            )

            answer = chatGPT_conversation(conversation)
            answer_content = answer.choices[0].message.content
            st.info(answer_content)

        else:

            st.info('계약서 PDF 와 질문 리스트를 업로드 해주세요')


