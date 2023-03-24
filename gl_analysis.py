import openai
import PyPDF2
import streamlit as st
import pandas as pd
import time

# streamlit run C:/gibeom/개인자료/!Projects/Digital/ChatGPT/python/contractanalysis/gl_analysis.py

openai.api_key = st.secrets["api_secret"]

st.title('Assurance DA')
st.header('GL 분석기')
st.markdown("<div style='text-align: right;'>Developed by Assurance DA (문의 : <a href = \"mailto:jae-dong.kim@pwc.com\">gibeom.kim@pwc.com</a>)</div>", unsafe_allow_html=True)
st.write("")
st.markdown("<br>", unsafe_allow_html=True)

st.write('GL을 업로드하고 무엇이든 물어보세요!')

file_gl = None
file_gl = st.file_uploader("파일을 선택하세요(xlsx만 가능)", type=['xlsx'])

conversation = []


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


def get_data_from_xlsx(file):
    df = pd.read_excel(file)

    df_columns = df.columns

    df_columns = [e.strip().replace(' ', '') for e in df_columns]

    df_columns_customer = [e for e in df_columns if '거래처' in e or '고객' in e]
    df_columns_account = [e for e in df_columns if '계정' in e]
    df_columns_amount = [e for e in df_columns if '금액' in e]
    df_columns_text = [e for e in df_columns if '텍스트' in e or '적요' in e or '헤더텍스트' in e]

    options_customer = st.multiselect(
        '거래처 관련 열이름을 1개만 선택하세요',
        df_columns,
        df_columns_customer)

    options_account = st.multiselect(
        '계정 관련 열이름을 1개만 선택하세요',
        df_columns,
        df_columns_account)

    options_amount = st.multiselect(
        '금액 관련 열이름을 1개만 선택하세요',
        df_columns,
        df_columns_amount)

    options_text = st.multiselect(
        '적요 관련 열이름을 1개만 선택하세요',
        df_columns,
        df_columns_text)

    result = {
        'data': df,
        'header_original': df.columns,
        'header_refined': df_columns,
        'header_customer': options_customer,
        'header_account': options_account,
        'header_amount': options_amount,
        'header_text': options_text
    }

    st.write('"거래처"와 "금액" 열머리는 반드시 선택되어야 합니다')

    return result


if file_gl is not None:

    options_dict = get_data_from_xlsx(file_gl)

    data = options_dict['data']
    header_original = options_dict['header_original']
    header_refined = options_dict['header_refined']
    header_customer = options_dict['header_customer']
    header_account = options_dict['header_account']
    header_amount = options_dict['header_amount']
    header_text = options_dict['header_text']

    if not len(header_customer) == 1:
        st.write('거래처에 해당하는 열이름을 1개만 선택하세요')
    if not len(header_amount) == 1:
        st.write('계정에 해당하는 열이름을 1개만 선택하세요')
    if not len(header_amount) == 1:
        st.write('금액에 해당하는 열이름을 1개만 선택하세요')
    if not len(header_text) == 1:
        st.write('적요에 해당하는 열이름을 1개만 선택하세요')

    if len(header_customer) == 1 and len(header_account) == 1 and len(header_amount) == 1:
        index_customer = [header_refined.index(e) for e in header_customer]
        index_account = [header_refined.index(e) for e in header_account]
        index_amount = [header_refined.index(e) for e in header_amount]
        index_text = [header_refined.index(e) for e in header_text]

        original_header_customer = [header_original[e] for e in index_customer]
        original_header_account = [header_original[e] for e in index_account]
        original_header_amount = [header_original[e] for e in index_amount]
        original_header_text = [header_original[e] for e in index_text]

        for header in original_header_account + original_header_customer + original_header_text:
            data[header] = data[header].fillna('Null')

        pivot_df = pd.pivot_table(
            data=data,
            index=original_header_account + original_header_customer + original_header_text,
            values=original_header_amount
        )

        print(data)
        print(original_header_account + original_header_customer + original_header_text)
        print(original_header_amount)
        print(pivot_df)

        st.write(pivot_df)

"""
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
"""

