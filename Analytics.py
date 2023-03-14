import openai
import streamlit as st
import pandas as pd
import io



openai.api_key = st.secrets["api_secret"]

st.title('Assurance DA')
st.header('AI Consultant - Analytics')
st.write('원장을 업로드하고 무엇이든 물어보세요!')
st.write('Developed by Assurance DA (jae-dong.kim@pwc.com)')



file = st.file_uploader("파일을 선택하세요(excel만 가능)", type = ['xlsx','xls'])

def get_text():
    input_text = st.text_input('해당 계정에 대하여 무엇이 궁금하신가요? ' , key ='input')
    return input_text

def chatGPT_conversation(conversation):
    response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo',
            messages = conversation
            
    )


    conversation.append({'role':response.choices[0].message.role, 'content':response.choices[0].message.content})
    return conversation





# file_name = '게임 (도급) 표준계약서.pdf'


if file is not None:
    df = pd.read_excel(file)

    
        

# pdf_file.close()




    conversation = []
    conversation.append({'role':'system','content':'다음 미수금 회계원장를 읽고 묻는 질문에 답변해줘'})
    # conversation = chatGPT_conversation(conversation)


    # print(conversation)

    k=0
    s = io.StringIO()
    df.to_csv(s, sep='\t')
    journal = s.getvalue()

    st.info(journal)


    conversation.append({"role": "system", "content": journal})
        # conversation = chatGPT_conversation(conversation)

    # 사용자의 입력 받기
    user_msg = st.text_input('계약서에 대하여 무엇이 궁금하신가요?')


    # 사용자의 입력이 있는 경우
    if st.button('질문 제출'):
        conversation.append({"role":"user","content":user_msg})
        conversation = chatGPT_conversation(conversation)
        answer = conversation[-1]['content']
        st.info(answer)





    # while True:
    #     k+=1
    #     user_msg = st.text_input('계약서에 대하여 무엇이 궁금하신가요? ' , key ='input'+str(k))
    #     if user_msg:

            
    #         conversation.append({"role":"user","content":user_msg})
    #         conversation = chatGPT_conversation(conversation)

    #         answer = conversation[-1]['content']
    #         st.write(answer)









          
    



