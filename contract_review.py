import openai
import PyPDF2
import streamlit as st
import time


openai.api_key = st.secrets["api_secret"]

st.title('Assurance DA')
st.header('AI Consultant - 계약서검토')
st.markdown("<div style='text-align: right;'>Developed by Assurance DA (문의 : <a href = \"mailto:jae-dong.kim@pwc.com\">jae-dong.kim@pwc.com</a>)</div>", unsafe_allow_html=True)
st.write("")
st.markdown("<br>", unsafe_allow_html=True)

st.write('계약서를 업로드하고 무엇이든 물어보세요!')



pdf_file = st.file_uploader("파일을 선택하세요(PDF만 가능)", type = ['pdf'])

def get_text():
    input_text = st.text_input('계약서에 대하여 무엇이 궁금하신가요? ' , key ='input')
    return input_text

def chatGPT_conversation(conversation):
    response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo',
            messages = conversation
            
    )


    conversation.append({'role':response.choices[0].message.role, 'content':response.choices[0].message.content})
    return conversation





# file_name = '게임 (도급) 표준계약서.pdf'


if pdf_file is not None:
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    n=0
    page_obj = []
    for page in range(len(pdf_reader.pages)):
        n +=1
        page_obj.append(pdf_reader.pages[page].extract_text())
        

# pdf_file.close()




    conversation = []
    conversation.append({'role':'system','content':'다음 계약서를 읽고 묻는 질문에 답변을 기재하고 답변을 찾을 수 있는 조항을 문장 마지막에 괄호안에 알려줘: '})
    # conversation = chatGPT_conversation(conversation)

    for i in range(4):
        conversation.append({"role": "system", "content": page_obj[i]})
        # conversation = chatGPT_conversation(conversation)

    # print(conversation)

#     k=0

    


    # 사용자의 입력 받기
    user_msg = st.text_input('계약서에 대하여 무엇이 궁금하신가요?')

    # 사용자의 입력이 있는 경우
    if st.button('질문 제출'):
        conversation.append({"role":"user","content":user_msg})
        conversation = chatGPT_conversation(conversation)
        answer = conversation[-1]['content']
        st.info(answer)

#     else:
#         time.sleep(120)






    # while True:
    #     k+=1
    #     user_msg = st.text_input('계약서에 대하여 무엇이 궁금하신가요? ' , key ='input'+str(k))
    #     if user_msg:

            
    #         conversation.append({"role":"user","content":user_msg})
    #         conversation = chatGPT_conversation(conversation)

    #         answer = conversation[-1]['content']
    #         st.write(answer)









          
    



