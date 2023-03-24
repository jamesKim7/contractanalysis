# -*- coding: utf-8 -*-
import pandas as pd

import dsd_handler
from bs4 import BeautifulSoup as bs
import re
from difflib import SequenceMatcher
import streamlit as st
import io
import openai

openai.api_key = st.secrets["api_secret"]

DSDHandler = dsd_handler.DSDHandler()

st.set_page_config(layout="wide")

st.title('Assurance DA')
st.header('Disclosure checklist with ChatGPT')
st.write('dsd 파일을 업로드하고 ChatGPT 를 활용하여 Disclosure checklist 를 작성하세요')
st.write('Developed by Assurance DA (gibeom.kim@pwc.com)')

file = st.file_uploader(
    "파일을 선택하세요(DSD만 가능)",
    type=['dsd']
)

if file is not None:

    file_name = file.name

    dsd_path = r"C:\gibeom\개인자료\!Projects\케이티스카이라이프\01. DSD\20230309 별도, 연결\FY2022 케이티스카이라이프 별도감사보고서_v3.2.dsd"

    xml_list = DSDHandler.open_dsd_file(mode='edited', file_byte=file.read())

    contents_raw_xml = [e for e in xml_list if e['name'] == 'contents.xml'][0]['raw_xml']

    soup = bs(contents_raw_xml, 'html.parser')

    # 태그 구조 분석 Document 태그로 시작

    tag_list = []

    def table_tag_to_list(table_tag):

        data = []

        table_head = table_tag.find('thead')

        if table_head:
            rows = table_head.find_all('tr')

            for row in rows:
                cols = row.find_all('th')
                # cols = [[re.compile('[가-힝]').findall(ele.text)[0] for ele in col if re.compile('[가-힝]').findall(ele.text)] for col in cols]

                new_row = []

                for col in cols:

                    new_row.append(col.text)

                if new_row:
                    data.append(new_row)

        table_body = table_tag.find('tbody')

        if table_body:
            rows = table_body.find_all('tr')

            for row in rows:
                cols = row.find_all(['tu', 'td'])
                # cols = [[re.compile('[가-힝]').findall(ele.text)[0] for ele in col if re.compile('[가-힝]').findall(ele.text)] for col in cols]

                new_row = []

                for col in cols:

                    col_text = col.text
                    try:
                        try:
                            col_value = int(col_text.strip().replace(',', ''))
                        except:
                            col_value = float(col_text.strip().replace(',', ''))

                    except:
                        col_value = col_text.replace('\u3000', '')

                    new_row.append(col_value)

                if new_row:
                    data.append(new_row)

        return data

    def find_all_child_seperate_text_table(tag):

        if tag.name == 'table':
            data = table_tag_to_list(tag)

            tag_list.append({
                'tag': tag.name,
                'data': data
            })

        else:
            tag_text = tag.find(text=True)

            if tag_text and tag_text.strip():

                # &cr 줄바꿈 처리
                and_cr_list = [e for e in tag_text.split('&cr;') if e]
                result_list = []
                for e in and_cr_list:
                    for e2 in e.split('cr;'):
                        if e2.strip():
                            result_list.append(e2)

                for paragraph in result_list:
                    tag_list.append({
                        'tag': tag.name,
                        'data': paragraph
                    })

            children = tag.find_all(recursive=False)

            if children:
                for child_tag in children:
                    find_all_child_seperate_text_table(child_tag)

    def run_sentiment_analysis(txt):
        return txt + 'got it'

    first_tag = soup.find()

    find_all_child_seperate_text_table(first_tag)

    # 삭제하는 태그
    for i in list(reversed(range(len(tag_list)))):
        if tag_list[i]['tag'] in ['warning', 'extraction', 'comment', 'librarylist']:
            del tag_list[i]

    # title 태그 주석 찾기

    index_표지_마지막 = 0
    index_주석_시작 = 0
    index_외부감사실시내용_시작 = 0

    for i, tag in enumerate(tag_list):
        if not index_표지_마지막 and tag['tag'] == 'table':
            for row in tag['data']:
                for e in row:
                    if isinstance(e, str) and e.replace(' ', '').find('(전화)') != -1:
                        index_표지_마지막 = i
                        print(f'\n표지 마지막 line 찾음 : {index_표지_마지막}')

        if tag['tag'] == 'title' and tag['data'] == '주석':
            index_주석_시작 = i
            print(f'\n주석 line 찾음 : {index_주석_시작}')

        if tag['tag'] == 'title' and tag['data'].strip().replace(' ', '') == '외부감사실시내용':
            index_외부감사실시내용_시작 = i
            print(f'\nindex_외부감사실시내용_시작 line 찾음 : {index_외부감사실시내용_시작}')
            break

    if index_표지_마지막 and index_주석_시작:

        # document 구분
        for i in range(len(tag_list)):
            if i <= index_표지_마지막:
                tag_list[i]['document_type'] = 'Intro'
            elif i < index_주석_시작:
                tag_list[i]['document_type'] = 'FS'
            elif i < index_외부감사실시내용_시작:
                tag_list[i]['document_type'] = 'FN'
            else:
                tag_list[i]['document_type'] = '외부감사실시내용'

        # FS keywords
        fs_keywords = {
            'BS': ['자산', '유동자산', '현금및현금성자산', '매출채권및기타채권', '금융리스채권', '기타금융자산', '재고자산', '당기법인세자산', '기타유동자산', '비유동자산',
                   '비유동매출채권및기타채권', '장기금융리스채권', '비유동기타금융자산', '유형자산', '투자부동산', '무형자산', '사용권자산', '관계기업및공동기업투자', '이연법인세자산',
                   '확정급여자산', '기타비유동자산', '자산총계', '부채', '유동부채', '매입채무및기타채무', '단기차입금', '유동리스부채', '유동충당부채', '당기법인세부채', '기타유동부채',
                   '비유동부채', '장기매입채무및기타채무', '장기차입금', '비유동리스부채', '순확정급여부채', '비유동충당부채', '이연법인세부채', '기타비유동부채', '부채총계', '자본',
                   '지배기업의소유주지분', '자본금', '주식발행초과금', '이익잉여금', '기타포괄손익누계액', '기타자본구성요소', '비지배지분:', '비지배지분', '자본총계', '부채와자본총계'],
            'PL': ['영업수익', '영업비용', '영업이익', '기타손익', '기타수익', '기타비용', '금융손익', '금융수익', '금융비용', '관계기업순손익지분', '법인세비용차감전순이익',
                   '법인세비용', '당기순이익', '지배기업소유주지분', '비지배지분', '주당이익', '기본주당순이익', '희석주당순이익'],
            'PL_OCI': ['당기순이익', '당기세후기타포괄이익(손실)', '후속적으로당기손익으로재분류되지않는항목', '확정급여제도의재측정요소', '지분법이익잉여금변동',
                       '기타포괄손익-공정가치측정금융자산평가손익', '당기총포괄이익', '지배기업소유주지분', '비지배지분'],
            'CE': ['총포괄이익', '당기순이익', '기타포괄손익공정가치측정금융자산평가손익', '확정급여제도의재측정요소', '지분법이익잉여금변동', '주주와의거래', '연차배당', '자기주식의처분',
                   '전환사채전환권의행사', '종속기업지분변동차액', '총포괄이익', '당기순이익', '기타포괄손익-공정가치측정금융자산평가손익', '확정급여제도의재측정요소', '지분법이익잉여금변동',
                   '주주와의거래', '연차배당', '자기주식의취득', '자기주식의처분', '사업결합으로인한자본변동'],
            'CF': ['영업활동으로인한현금흐름', '영업에서창출된현금흐름', '당기순이익', '조정', '영업활동으로인한자산부채의변동', '이자수취', '이자지급', '배당금의수취', '법인세납부액',
                   '투자활동으로인한현금흐름', '투자활동으로인한현금유입액', '유동상각후원가측정금융자산의처분', '유동당기손익-공정가치측정금융자산의처분', '단기대여금의감소', '유동임차보증금의감소',
                   '장기대여금의감소', '비유동임차보증금의감소', '토지의처분', '방송기계의처분', '방송수신장치의처분', '인터넷장비의처분', '공구기구비품의처분', '차량운반구의처분',
                   '건설중인자산의처분', '', '관계기업투자의처분', '사업결합으로인한순현금유입', '투자활동으로인한현금유출액', '유동상각후원가측정금융자산의취득', '방송기계의취득',
                   '방송수신장치의취득', '인터넷장비의취득', '공구기구비품의취득', '차량운반구의취득', '건설중인자산의취득', '투자부동산(건물)의취득', '방송프로그램의취득', '기타의무형자산의취득',
                   '회원권의취득', '관계기업투자의취득', '사업결합으로인한순현금유출', '재무활동으로인한현금흐름', '재무활동으로인한현금유입액', '차입금의증가', '사채의발행',
                   '재무활동으로인한현금유출액', '차입금의상환', '리스부채의상환', '배당금의지급', '보통주의발행', '외화환산으로인한현금의변동', '현금의증가(감소)', '기초의현금및현금성자산',
                   '기말의현금및현금성자산']
        }

        fs_keywords_ratio_dict = {
            'BS': [],
            'PL': [],
            'PL_OCI': [],
            'CE': [],
            'CF': []
        }

        # table 태크에서 BS, PL, CE, CF 찾기

        target_table = []
        target_table_only_hangul = []

        for i, tag in enumerate(tag_list):

            if tag['document_type'] == 'FS' and tag['tag'] == 'table':
                target_table.append([i, tag])

        for table_list in target_table:

            table_index = table_list[0]
            table_tag_data = table_list[1]['data']
            table_tag_data_only_hangul = []
            for row in table_tag_data:
                new_row = []
                for e in row:
                    only_hangul = ''.join(re.compile('[가-힝]').findall(str(e)))
                    if only_hangul:
                        new_row.append(only_hangul)
                if new_row:
                    table_tag_data_only_hangul.append(new_row)

            target_table_only_hangul.append([table_index, table_tag_data_only_hangul])

        for fs_type in fs_keywords.keys():

            for table_data in target_table_only_hangul:

                data = table_data[1]

                keyword_highest_ratio = []

                for keyword in fs_keywords[fs_type]:
                    highest_ratio = 0

                    for row in data:
                        for ele in row:
                            ratio = SequenceMatcher(None, keyword, ele).ratio()
                            highest_ratio = max(highest_ratio, ratio)

                    keyword_highest_ratio.append(highest_ratio)

                average_ratio = round(sum(keyword_highest_ratio) / len(keyword_highest_ratio), 3)

                fs_keywords_ratio_dict[fs_type].append(average_ratio)

        for fs_type in fs_keywords.keys():
            maximum_ratio = max(fs_keywords_ratio_dict[fs_type])
            maximum_ratio_index = fs_keywords_ratio_dict[fs_type].index(maximum_ratio)
            tag_list_index = target_table_only_hangul[maximum_ratio_index][0]

            print(f'\n가장 {fs_type} 과 유사한 테이블')
            print(fs_type, maximum_ratio, maximum_ratio_index, tag_list_index)

            if 'fs_type' not in tag_list[tag_list_index].keys():
                tag_list[tag_list_index]['fs_type'] = fs_type
                tag_list[tag_list_index]['fs_type_ratio'] = maximum_ratio
                tag_list[tag_list_index]['fs_type_sub'] = ['main_table']
            else:
                if maximum_ratio > tag_list[tag_list_index]['fs_type_ratio']:
                    tag_list[tag_list_index]['fs_type'] = fs_type
                    tag_list[tag_list_index]['fs_type_ratio'] = maximum_ratio
                    tag_list[tag_list_index]['fs_type_sub'] = ['main_table']

        # FS 부속 표 분류

        fs_keyword_list = [
            {'text': '재무상태표', 'fs_type': 'BS'},
            {'text': '포괄손익계산서', 'fs_type': 'PL_OCI'},
            {'text': '손익계산서', 'fs_type': 'PL'},
            {'text': '자본변동표', 'fs_type': 'CE'},
            {'text': '현금흐름표', 'fs_type': 'CF'}
        ]
        for i, tag in enumerate(tag_list):
            if tag['document_type'] == 'FS':
                if 'fs_type' not in tag.keys():
                    if tag['tag'] == 'table':
                        for row in tag['data']:
                            for e in row:
                                for fs_keyword_dict in fs_keyword_list:
                                    fs_keyword_text = fs_keyword_dict['text']
                                    fs_keyword_fs_type = fs_keyword_dict['fs_type']
                                    if e.strip().replace(' ', '').find(fs_keyword_text) != -1:
                                        tag_list[i]['fs_type'] = fs_keyword_fs_type
                                        if 'fs_type_sub' not in tag_list[i].keys():
                                            tag_list[i]['fs_type_sub'] = ['title_table']
                                            break
                                        else:
                                            if 'title_table' not in tag_list[i]['fs_type_sub']:
                                                tag_list[i]['fs_type_sub'].append('title_table')
                                                break

                                if e.strip().replace(' ', '').find('단위') != -1:
                                    if 'fs_type_sub' not in tag_list[i].keys():
                                        tag_list[i]['fs_type_sub'] = ['unit_table']
                                    else:
                                        if 'unit_table' not in tag_list[i]['fs_type_sub']:
                                            tag_list[i]['fs_type_sub'].append('unit_table')

                                    if 'fs_type' not in tag_list[i].keys():
                                        if 'main_table' in tag_list[i + 1]['fs_type_sub']:
                                            tag_list[i]['fs_type'] = tag_list[i + 1]['fs_type']

                                if e.strip().replace(' ', '').find('별첨') != -1 or e.strip().replace(' ', '').find('재무제표') != -1:
                                    if 'fs_type_sub' not in tag_list[i].keys():
                                        tag_list[i]['fs_type_sub'] = ['fn_comment_table']
                                    else:
                                        if 'fn_comment_table' not in tag_list[i]['fs_type_sub']:
                                            tag_list[i]['fs_type_sub'].append('fn_comment_table')

                                    if 'fs_type' not in tag_list[i].keys():
                                        if 'main_table' in tag_list[i - 1]['fs_type_sub']:
                                            tag_list[i]['fs_type'] = tag_list[i - 1]['fs_type']

        # FS 숫자 분류

        for i, tag in enumerate(tag_list):
            if tag['document_type'] == 'FN':
                if tag['tag'] != 'table' and isinstance(tag['data'], str):
                    # 주요 번호 추출
                    if re.match('\d+\.+ *[a-zA-Z가-힣]+', tag['data']):
                        tag_list[i]['fn_num'] = int(tag['data'].split('.')[0])
                        tag_list[i]['fn_name'] = tag['data'].split('.')[1].strip()
                        tag_list[i]['fn_sub_type'] = ['main_title']

                    # 서브 번호 추출
                    elif re.match('\d+\.+\d+ *[a-zA-Z가-힣]+', tag['data']):
                        temp_str = tag['data'].split('.')[1]
                        result_num = ''
                        result_name = ''
                        for index_str, e in enumerate(temp_str):
                            if e.isnumeric():
                                result_num += e
                            else:
                                result_name = temp_str[index_str:]
                                break
                        tag_list[i]['fn_sub_num'] = int(result_num)
                        tag_list[i]['fn_sub_name'] = result_name
                        tag_list[i]['fn_sub_type'] = ['sub_title']
                    else:
                        tag_list[i]['fn_sub_type'] = ['paragraph']
                else:
                    tag_list[i]['fn_sub_type'] = ['table']

                # 메인 번호 업데이트
                if 'fn_num' not in tag_list[i].keys() and 'fn_num' in tag_list[i-1].keys():
                    tag_list[i]['fn_num'] = tag_list[i-1]['fn_num']
                if 'fn_name' not in tag_list[i].keys() and 'fn_name' in tag_list[i-1].keys():
                    tag_list[i]['fn_name'] = tag_list[i-1]['fn_name']

                # 서브번호는 메인번호가 같을 경우에만 참조
                if 'fn_num' in tag_list[i-1].keys() and 'fn_num' in tag_list[i].keys() and \
                        tag_list[i]['fn_num'] == tag_list[i-1]['fn_num']:
                    if 'fn_sub_num' not in tag_list[i].keys() and 'fn_sub_num' in tag_list[i-1].keys():
                        tag_list[i]['fn_sub_num'] = tag_list[i-1]['fn_sub_num']
                    if 'fn_sub_name' not in tag_list[i].keys() and 'fn_sub_name' in tag_list[i-1].keys():
                        tag_list[i]['fn_sub_name'] = tag_list[i-1]['fn_sub_name']

        col1, col2, col3 = st.columns(3)

        paragraph_list = []
        paragraph_checkbox_list = []
        target_paragraph_list = []
        target_tag_index_list = []

        with col1:

            st.subheader('DSD 문단')

            with st.expander('보고서 커버'):
                for tag in tag_list:
                    if tag['document_type'] == 'Intro':
                        if isinstance(tag['data'], str):
                            st.write(tag['data'])
                        elif isinstance(tag['data'], list):
                            st.dataframe(data=pd.DataFrame(tag['data']))

            with st.expander('BS'):
                for tag in tag_list:
                    if tag['document_type'] == 'FS' and tag['fs_type'] == 'BS':
                        if isinstance(tag['data'], str):
                            st.write(tag['data'])
                        elif isinstance(tag['data'], list):
                            hide_dataframe_row_index = """
                                        <style>
                                        .row_heading.level0 {display:none}
                                        .blank {display:none}
                                        </style>
                                        """
                            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                            st.dataframe(data=pd.DataFrame(tag['data']).style.format(thousands=","))

            with st.expander('PL'):
                for tag in tag_list:
                    if tag['document_type'] == 'FS' and tag['fs_type'] == 'PL':
                        if isinstance(tag['data'], str):
                            st.write(tag['data'])
                        elif isinstance(tag['data'], list):
                            st.dataframe(data=pd.DataFrame(tag['data']))

            with st.expander('PL_OCI'):
                for tag in tag_list:
                    if tag['document_type'] == 'FS' and tag['fs_type'] == 'PL_OCI':
                        if isinstance(tag['data'], str):
                            st.write(tag['data'])
                        elif isinstance(tag['data'], list):
                            st.dataframe(data=pd.DataFrame(tag['data']))

            with st.expander('CE'):
                for tag in tag_list:
                    if tag['document_type'] == 'FS' and tag['fs_type'] == 'CE':
                        if isinstance(tag['data'], str):
                            st.write(tag['data'])
                        elif isinstance(tag['data'], list):
                            st.dataframe(data=pd.DataFrame(tag['data']))

            with st.expander('CF'):
                for tag in tag_list:
                    if tag['document_type'] == 'FS' and tag['fs_type'] == 'CF':
                        if isinstance(tag['data'], str):
                            st.write(tag['data'])
                        elif isinstance(tag['data'], list):
                            st.dataframe(data=pd.DataFrame(tag['data']))

            for tag in tag_list:
                if tag['document_type'] == 'FN' and 'main_title' in tag['fn_sub_type']:
                    target_fn_num = tag['fn_num']
                    target_fn_name = tag['fn_name']
                    target_fn_num_name = f'{target_fn_num} {target_fn_name}'
                    with st.expander(target_fn_num_name):
                        for tag2 in tag_list:
                            if tag2['document_type'] == 'FN' and 'fn_num' in tag2.keys() and tag2['fn_num'] == target_fn_num:
                                if isinstance(tag2['data'], str):
                                        st.write(tag2['data'])
                                elif isinstance(tag2['data'], list):
                                    hide_dataframe_row_index = """
                                                <style>
                                                .row_heading.level0 {display:none}
                                                .blank {display:none}
                                                </style>
                                                """
                                    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                                    st.dataframe(data=pd.DataFrame(tag2['data']).style.format(thousands=","))


        with col2:
            st.subheader("문단 선택")

            for tag in tag_list:
                if 'fs_type' in tag.keys() and tag['fs_type'] in ['BS', 'PL', 'PL_OCI', 'CE', 'CF']:
                    if tag['fs_type'] not in paragraph_list:
                        paragraph_list.append(tag['fs_type'])
                elif 'fn_sub_type' in tag.keys() and 'main_title' in tag['fn_sub_type']:
                    if tag['data'] not in paragraph_list:
                        paragraph_list.append(tag['data'])

            if 'selected' not in st.session_state:
                st.session_state.selected = False
            if 'multiselected' not in st.session_state:
                st.session_state.multiselected = None
            if 'multiselected_index' not in st.session_state:
                st.session_state.multiselected_index = None

            keyword = st.text_input('찾을 키워드를 입력하시고 검색 버튼을 누르면, 해당 키워드가 검색되는 주석 문단이 선택됩니다')

            def reset():
                if not st.session_state.selected:
                    st.session_state.selected = True
                else:
                    st.session_state.selected = False

                print('keyword :', keyword)

                for index, tag in enumerate(tag_list):
                    if isinstance(tag['data'], str):
                        if keyword in tag['data']:
                            if 'fs_type' in tag.keys():
                                if tag['fs_type'] not in target_paragraph_list:
                                    target_paragraph_list.append(tag['fs_type'])
                                    target_tag_index_list.append(index)
                            elif 'fn_num' in tag.keys():
                                fn_num_name = f"{tag['fn_num']}. {tag['fn_name']}"
                                if fn_num_name not in target_paragraph_list:
                                    target_paragraph_list.append(fn_num_name)
                                    target_tag_index_list.append(index)
                    elif isinstance(tag['data'], list):
                        for row in tag['data']:
                            for ele in row:
                                if keyword in str(ele):
                                    if 'fs_type' in tag.keys():
                                        if tag['fs_type'] not in target_paragraph_list:
                                            target_paragraph_list.append(tag['fs_type'])
                                            target_tag_index_list.append(index)
                                    elif 'fn_num' in tag.keys():
                                        fn_num_name = f"{tag['fn_num']}. {tag['fn_name']}"
                                        if fn_num_name not in target_paragraph_list:
                                            target_paragraph_list.append(fn_num_name)
                                            target_tag_index_list.append(index)
                                    break

                print(target_paragraph_list)
                st.session_state.multiselected = target_paragraph_list
                st.session_state.multiselected_index = target_tag_index_list

            search_button = st.button('검색', on_click=reset)

            print(paragraph_list)
            print(st.session_state.multiselected)

            multipleselect = st.multiselect(
                'DSD 문단을 선택해주세요',
                options=paragraph_list,
                default=st.session_state.multiselected
            )

        with col3:
            st.subheader("ChatGPT")

            st.write('왼쪽 "Elements 선택" 에서 선택한 DSD 문단에 대해서 아래 기재한 내용을 ChatGPT에게 물어봅니다.\n물어볼 내용을 기재 후 물어보기 버튼을 눌러주세요')
            txt = st.text_area(
                label='ChatGPT 에 물어볼 내용을 입력하세요',
                height=500
            )
            if not st.button('물어보기'):
                caption = st.caption('''예시 : 

⑴ 기초자산 유형별 사용권자산의 감가상각비

⑵ 리스부채에 대한 이자비용

⑶ 문단 6을 적용하여 회계처리하는 단기리스에 관련되는 비용. 1개월 이하인 리스기간에 관련되는 비용은 이 비용에 포함할 필요가 없다.

⑷ 문단 6을 적용하여 회계처리하는 소액자산 리스에 관련되는 비용.문단 53⑶에 포함되는, 소액자산의 단기리스에 관련되는 비용은 이 비용에 포함하지 않는다.

⑸ 리스부채 측정치에 포함되지 않은 변동리스료에 관련되는 비용[참조: 결론도출근거 문단 BC217(3)]

54 다른 형식이 더 적절하지 않다면, 리스이용자는 표 형식으로 문단 53에서 규정하는 내용을 공시한다. 공시하는 금액에는 리스이용자가 보고기간 중에 다른 자산의 장부금액에 포함한 원가를 포함한다.

55 보고기간 말 현재 약정된 단기리스 포트폴리오가 문단 53⑶을 적용하여 공시하는 단기리스 비용에 관련되는 단기리스 포트폴리오와 다른 경우에, 리스이용자는 문단 6을 적용하여 회계처리하는 단기리스의 리스약정 금액을 공시한다.''')

            else:
                messages = []
                messages.append({"role": "system", "content": '너는 대한민국 공인회계사야'})
                print(st.session_state.multiselected_index)
                index_lease = []
                for index, tag in enumerate(tag_list):
                    if 'fn_name' in tag.keys() and tag['fn_name'] == '리스':
                        index_lease.append(index)
                print('index_lease: ', index_lease)
                for tag_index in index_lease:
                # for tag_index in st.session_state.multiselected_index:
                    if isinstance(tag_list[tag_index]['data'], str):
                        if 'fs_type' in tag_list[tag_index].keys():
                            content = f'<div><p>보고서 ID : {tag_list[tag_index]["fs_type"]}</p> <p>{tag_list[tag_index]["data"]}</p></div>'
                        elif 'fn_num' in tag_list[tag_index].keys():
                            content = f'<div><p>보고서 ID : {tag_list[tag_index]["fn_num"]}</p> <p>{tag_list[tag_index]["fn_name"]}] {tag_list[tag_index]["data"]}</p></div>'

                        messages.append({"role": "system", "content": content})

                    elif isinstance(tag_list[tag_index]['data'], list):
                        table_text = '<table>'

                        for row in tag_list[tag_index]['data']:

                            new_row = '<tr>'

                            for col in row:

                                new_row += f'<td>{str(col)}</td>'

                            new_row += '</tr>'

                            table_text += new_row

                        table_text += '</table>'

                        if 'fs_type' in tag_list[tag_index].keys():
                            content = f'<div><p>보고서 ID : {tag_list[tag_index]["fs_type"]}</p> {table_text}</div>'
                        elif 'fn_num' in tag_list[tag_index].keys():
                            content = f'<div><p>보고서 ID : {tag_list[tag_index]["fn_num"]}</p> {table_text}</div>'

                        messages.append({"role": "system", "content": content})
                messages.append({"role": "system", "content": '첨부한 HTML 형식의 보고서를 면밀히 점검해서 아래의 내용 중 공시가 된 내용과 되지 않은 내용을 알려줘.'})
                messages.append({"role": "system", "content": '알려줄 때 보고서 ID는 대괄호 안에 표시해서 알려줘.'})
                messages.append({"role": "user", "content": txt})

                print(messages)

                completions = openai.ChatCompletion.create(
                    model="gpt-4",
                    # model="gpt-3.5-turbo",
                    messages=messages
                )
                answer = completions.choices[0]['message']['content']
                st.write('답변:\n\n', answer)


