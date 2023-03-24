import openai
import PyPDF2
import streamlit as st
import pandas as pd
import time

from bs4 import BeautifulSoup


openai.api_key = st.secrets["api_secret"]

st.title('Assurance DA')
st.header('AI Consultant - HTML검토')
st.markdown("<div style='text-align: right;'>Developed by Assurance DA (문의 : <a href = \"mailto:gibeom.kim@pwc.com\">jae-dong.kim@pwc.com</a>)</div>", unsafe_allow_html=True)
st.write("")
st.markdown("<br>", unsafe_allow_html=True)

st.write('HTML를 업로드하고 무엇이든 물어보세요!')

html_file = st.file_uploader("파일을 선택하세요(HTML만 가능)", type=['html'])

dataframe = None

conversation = []
conversation.append(
    {
        'role': 'system',
        'content': '다음 html 파일을 읽고 묻는 질문에 답변을 기재하고 답변을 찾을 수 있는 조항을 문장 마지막에 괄호안에 알려줘: '
    }
)

def chatGPT_conversation(conversation_input):
    response = openai.ChatCompletion.create(
            model='gpt-4',
            # model='gpt-3.5-turbo',
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


if html_file is not None:

    soup = BeautifulSoup(html_file, features="html.parser")

    for target_tag in ['td', 'th']:

        for tag in soup.find_all(target_tag):
            tag.attrs.clear()

    soup_refined = str(soup)

    print(soup_refined)

    file_name = html_file.name

    conversation.append({"role": "system", "content": soup_refined})

    user_msg = st.text_input('계약서에 대하여 추가로 무엇이 궁금하신가요?')

    # 사용자의 입력이 있는 경우
    if st.button('기본 질문 제출'):

        if soup_refined is not None:

            ask_question(conversation, user_msg)


        else:

            pass

