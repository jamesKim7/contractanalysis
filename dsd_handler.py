# -*- coding: utf-8 -*-

import os
import zipfile
import bs4
bs = bs4.BeautifulSoup
import bs4
import io


class DSDHandler:

    def __init__(self):
        """
        self.path_default = f'{os.path.dirname(__file__)}/dsd'
        self.dsd_file_list = os.listdir(self.path_default)
        self.dsd_name_list = [file.replace('.dsd', '') for file in os.listdir(f'{self.path_default}\\original')]
        """
        pass

    def open_dsd_file(self, mode, file_name='', dsd_name='', file_path='', file_byte=None):
        # 기본서식파일 읽기
        if mode in ['original', 'with_triple_sharp']:
            # 기본서식파일 이름과 mapping 되는지 check
            if dsd_name in self.dsd_name_list:
                print('open', dsd_name)
                dsd_file_list = []
                with zipfile.ZipFile(f'{self.path_default}\\{mode}\\{dsd_name}.dsd', mode='r', compression=zipfile.ZIP_DEFLATED) as zf:
                    for file in zf.namelist():
                        with zf.open(file, mode='r') as f:
                            raw_xml = f.read().decode('utf-8')
                            data_bs = bs(raw_xml, 'xml')
                            new_dict = {
                                'name': file,
                                'raw_xml': raw_xml,
                                'data_bs': data_bs
                            }
                            dsd_file_list.append(new_dict)
                return dsd_file_list

            else:
                print('ERR: unknown file_name', file_name)
                raise

        elif mode == 'edited':
            dsd_file_list = []
            with zipfile.ZipFile(io.BytesIO(file_byte), mode='r', compression=zipfile.ZIP_DEFLATED) as zf:
            # with zipfile.ZipFile(file_path, mode='r', compression=zipfile.ZIP_DEFLATED) as zf:
                for file in zf.namelist():
                    if file.split('.')[-1] == 'xml':
                        with zf.open(file, mode='r') as f:
                            raw_xml = f.read().decode('utf-8')
                            data_bs = bs(raw_xml, 'xml')
                            new_dict = {
                                'name': file,
                                'raw_xml': raw_xml,
                                'data_bs': data_bs
                            }
                            dsd_file_list.append(new_dict)
            return dsd_file_list

        else:
            print('ERR: unknown mode', mode)
            raise

    def make_triple_sharp_dsd(self):

        # 대표이사 성명에 직급도 포함되도록 수정 필요
        """
        ### 변수의 종류는 아래와 같음

        ###FN : FN xml 들어갈 위치
        ###FS : FS xml 들어갈 위치
        ###COMPANY_NAME : 회사명
        ###COVER_COMPANY_NAME : Cover 페이지에 들어갈 회사명 회사명 앞에 가운데 정렬 위한 whitespace 필요
        ###COMPANY_LOCATION : 회사주소
        ###COMPANY_PHONE_NUMBER : 회사 전화번호
        ###PRESIDENT_NAME : 대표이사 성명
        ###GI_NOW : 당기 기
        ###GI_1_BEFORE : 전기 기
        ###FY_NOW_S : 당기초 일자
        ###FY_NOW : 당기말 일자
        ###FY_1_BEFORE_S : 전기초 일자
        ###FY_1_BEFORE : 전기말 일자
        ###FY_1_BEFORE_OE : 전기 온기말 일자
        
        """

        tag_location_descriptions = [
            # ###COVER_COMPANY_NAME
            {
                'variable_name': '###COVER_COMPANY_NAME',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '분기감사보고서', '분기검토보고서'],
                'tag_name': 'P',
                'attr_dict': {'USERMARK': 'F-18'},
                'tag_attr_matched_len': 3,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': '감사대상회사의명칭'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': '감사대상회사의명칭'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': '반기검토대상회사의명칭'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': '감사대상회사의명칭'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': '분기검토대상회사의명칭'},
                ],
                'parent_tag_name': 'COVER',
                'parent_tag_attr_dict': {},
                'sibling_before_tag_name': 'P',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '&cr;',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '&cr;&cr;&cr;',
                'matched_len': 1
            },
            # ###COVER_COMPANY_NAME와 그 종속회사
            {
                'variable_name': '###COVER_COMPANY_NAME와 그 종속회사',
                'target_dsd_name': ['반기연결감사보고서', '반기연결검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'P',
                'attr_dict': {'USERMARK': 'F-18'},
                'tag_attr_matched_len': 3,
                'string_list': [
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': '반기연결대상회사의명칭'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': '반기검토대상회사의명칭'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': '분기감사대상회사의명칭'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': '분기검토대상회사의명칭'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXX주식회사와그종속회사'}
                ],
                'parent_tag_name': 'COVER',
                'parent_tag_attr_dict': {},
                'sibling_before_tag_name': 'P',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '&cr;',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '&cr;&cr;&cr;',
                'matched_len': 1
            },

            # ###COMPANY_NAME
            {
                'variable_name': '###COMPANY_NAME',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '분기감사보고서', '분기검토보고서'],
                'tag_name': 'TD',
                'attr_dict': {'ALIGN': 'CENTER', 'VALIGN': 'MIDDLE', 'WIDTH': '600', 'HEIGHT': '39', 'USERMARK': 'F-14 B'},
                'tag_attr_matched_len': 1,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XX주식회사'},
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###COMPANY_NAME와 그 종속회사
            {
                'variable_name': '###COMPANY_NAME와 그 종속회사',
                'target_dsd_name': ['반기연결감사보고서', '반기연결검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {'ALIGN': 'CENTER', 'VALIGN': 'MIDDLE', 'WIDTH': '600', 'HEIGHT': '39', 'USERMARK': 'F-14 B'},
                'tag_attr_matched_len': 1,
                'string_list': [
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XX주식회사'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XX주식회사'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###COMPANY_NAME 대표이사 ###PRESIDENT_NAME
            {
                'variable_name': '###COMPANY_NAME 대표이사 ###PRESIDENT_NAME',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {'ALIGN': 'CENTER', 'VALIGN': 'MIDDLE', 'WIDTH': '600', 'HEIGHT': '30'},
                'tag_attr_matched_len': 2,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XX주식회사대표이사XXX'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XX주식회사대표이사XXX'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###COMPANY_NAME 주석
            {
                'variable_name': '###COMPANY_NAME',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '분기감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {'WIDTH': '600', 'HEIGHT': '30'},
                'tag_attr_matched_len': 5,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': '회사명:XXXX'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': '회사명:XXXX'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': '회사명:XXXX'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###COMPANY_NAME 주석
            {
                'variable_name': '###COMPANY_NAME',
                'target_dsd_name': ['반기검토보고서', '분기검토보고서'],
                'tag_name': 'TD',
                'attr_dict': {'WIDTH': '600', 'HEIGHT': '30'},
                'tag_attr_matched_len': 7,
                'string_list': [
                    {'dsd_name': '반기검토보고서', 'string_alpha': '회사명:XXXX'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': '회사명:XXXX'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###COMPANY_NAME와 그 종속회사 주석
            {
                'variable_name': '###COMPANY_NAME와 그 종속회사',
                'target_dsd_name': ['반기연결감사보고서', '분기연결감사보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {'WIDTH': '600', 'HEIGHT': '30'},
                'tag_attr_matched_len': 5,
                'string_list': [
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': '회사명:XXXX'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': '회사명:XXXX'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': '회사명:XXXX'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###COMPANY_NAME와 그 종속회사 주석
            {
                'variable_name': '###COMPANY_NAME와 그 종속회사',
                'target_dsd_name': ['반기연결검토보고서', '분기연결검토보고서'],
                'tag_name': 'TD',
                'attr_dict': {'WIDTH': '600', 'HEIGHT': '30'},
                'tag_attr_matched_len': 7,
                'string_list': [
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': '회사명:XXXX'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': '회사명:XXXX'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###GI_NOW
            {
                'variable_name': '###GI_NOW',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'CLASS': 'NORMAL',
                    'VALIGN': 'MIDDLE',
                    'WIDTH': '600',
                    'HEIGHT': '34',
                    'COLSPAN': '2',
                    'ALIGN': 'CENTER',
                    'USERMARK': 'F-BT14'
                },
                'tag_attr_matched_len': 2,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': '제XX기'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': '제XX기'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 2
            },

            # ###GI_1_BEFORE
            {
                'variable_name': '###GI_1_BEFORE',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'VALIGN': 'MIDDLE',
                    'WIDTH': '600',
                    'HEIGHT': '34',
                    'COLSPAN': '2',
                    'ALIGN': 'CENTER',
                    'USERMARK': 'F-BT14'
                },
                'tag_attr_matched_len': 4,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': '제XX기'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': '제XX기반기'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': '제XX기분기'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': '제XX기'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 2
            },

            # ###FY_NOW_S COVER
            {
                'variable_name': '###FY_NOW_S',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TU',
                'attr_dict': {
                    'CLASS': 'NORMAL',
                    'ALIGN': 'RIGHT',
                    'VALIGN': 'MIDDLE',
                    'WIDTH': '342',
                    'HEIGHT': '30',
                    'AUNIT': 'PERIODFROM',
                    'AUNITVALUE': ''
                },
                'tag_attr_matched_len': 1,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'TD',
                'sibling_next_tag_attr_dict': {'CLASS': 'NORMAL', 'VALIGN': 'MIDDLE', 'WIDTH': '258', 'HEIGHT': '30', 'AUPDATECONT': 'N'},
                'sibling_next_tag_string': '부터',
                'matched_len': 1
            },

            # ###FY_NOW COVER
            {
                'variable_name': '###FY_NOW',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TU',
                'attr_dict': {
                    'CLASS': 'NORMAL',
                    'ALIGN': 'RIGHT',
                    'WIDTH': '342',
                    'HEIGHT': '30',
                    'AUNIT': 'PERIODTO',
                    'AUNITVALUE': ''
                },
                'tag_attr_matched_len': 1,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'TD',
                'sibling_next_tag_attr_dict': {'CLASS': 'NORMAL', 'WIDTH': '258', 'HEIGHT': '30', 'AUPDATECONT': 'N'},
                'sibling_next_tag_string': '까지',
                'matched_len': 1
            },

            # ###FY_NOW_S 재무제표
            {
                'variable_name': '###FY_NOW_S',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TU',
                'attr_dict': {
                    'CLASS': 'NORMAL',
                    'ALIGN': 'RIGHT',
                    'VALIGN': 'MIDDLE',
                    'WIDTH': '342',
                    'HEIGHT': '30',
                    'AUNIT': 'PERIODFROM2',
                    'AUNITVALUE': ''
                },
                'tag_attr_matched_len': 1,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'TD',
                'sibling_next_tag_attr_dict': {'CLASS': 'NORMAL', 'VALIGN': 'MIDDLE', 'WIDTH': '258', 'HEIGHT': '30', 'AUPDATECONT': 'N'},
                'sibling_next_tag_string': '부터',
                'matched_len': 1
            },

            # ###FY_NOW 재무제표
            {
                'variable_name': '###FY_NOW',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TU',
                'attr_dict': {
                    'CLASS': 'NORMAL',
                    'ALIGN': 'RIGHT',
                    'WIDTH': '342',
                    'HEIGHT': '30',
                    'AUNIT': 'PERIODTO2',
                    'AUNITVALUE': ''
                },
                'tag_attr_matched_len': 1,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'TD',
                'sibling_next_tag_attr_dict': {'CLASS': 'NORMAL', 'WIDTH': '258', 'HEIGHT': '30', 'AUPDATECONT': 'N'},
                'sibling_next_tag_string': '까지',
                'matched_len': 1
            },

            # ###FY_1_BEFORE_S COVER 재무제표
            {
                'variable_name': '###FY_1_BEFORE_S',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'WIDTH': '342',
                    'HEIGHT': '30',
                    'ALIGN': 'RIGHT',
                    'VALIGN': 'MIDDLE'
                },
                'tag_attr_matched_len': 2,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'TD',
                'sibling_next_tag_attr_dict': {'WIDTH': '258', 'HEIGHT': '30', 'VALIGN': 'MIDDLE'},
                'sibling_next_tag_string': '부터',
                'matched_len': 2
            },

            # ###FY_1_BEFORE COVER 재무제표
            {
                'variable_name': '###FY_1_BEFORE',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'WIDTH': '342',
                    'HEIGHT': '30',
                    'ALIGN': 'RIGHT'
                },
                'tag_attr_matched_len': 4,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'TD',
                'sibling_next_tag_attr_dict': {'WIDTH': '258', 'HEIGHT': '30'},
                'sibling_next_tag_string': '까지',
                'matched_len': 2
            },

            # ###GI_NOW : ###FY_NOW 현재 주석
            {
                'variable_name': '###GI_NOW : ###FY_NOW 현재',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'ALIGN': 'CENTER',
                    'WIDTH': '600',
                    'HEIGHT': '30'
                },
                'tag_attr_matched_len': 4,
                'string_list': [
                    {'dsd_name': '감사보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '반기감사보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '반기검토보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '반기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '반기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '분기감사보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '분기검토보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '분기연결감사보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '분기연결검토보고서', 'string_alpha': 'XXXX년XX월XX일현재'},
                    {'dsd_name': '연결감사보고서', 'string_alpha': 'XXXX년XX월XX일현재'}
                ],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###GI_1_BEFORE : ###FY_1_BEFORE_OE 현재 주석
            {
                'variable_name': '###GI_1_BEFORE_OE : ###FY_1_BEFORE_OE 현재',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기연결감사보고서', '분기감사보고서', '분기연결감사보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'WIDTH': '600',
                    'HEIGHT': '30'
                },
                'tag_attr_matched_len': 5,
                'string_list': [],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###GI_1_BEFORE : ###FY_1_BEFORE_OE 현재 주석
            {
                'variable_name': '###GI_1_BEFORE_OE : ###FY_1_BEFORE_OE 현재',
                'target_dsd_name': ['반기검토보고서', '반기연결검토보고서', '분기검토보고서', '분기연결검토보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'WIDTH': '600',
                    'HEIGHT': '30'
                },
                'tag_attr_matched_len': 7,
                'string_list': [],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'Y', 'ADELETE': 'Y'},
                'sibling_before_tag_name': '',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###COMPANY_PHONE_NUMBER
            {
                'variable_name': '###COMPANY_PHONE_NUMBER',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'WIDTH': '392',
                    'HEIGHT': '30',
                    'VALIGN': 'MIDDLE'
                },
                'tag_attr_matched_len': 2,
                'string_list': [],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': 'TD',
                'sibling_before_tag_attr_dict': {'WIDTH': '108', 'HEIGHT': '30', 'VALIGN': 'MIDDLE', 'ALIGN': 'CENTER', 'AUPDATECONT': 'N'},
                'sibling_before_tag_string': '(전화)',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###COMPANY_LOCATION
            {
                'variable_name': '###COMPANY_LOCATION',
                'target_dsd_name': ['감사보고서', '반기감사보고서', '반기검토보고서', '반기연결감사보고서', '반기연결검토보고서', '분기감사보고서', '분기검토보고서', '분기연결감사보고서', '분기연결검토보고서', '연결감사보고서'],
                'tag_name': 'TD',
                'attr_dict': {
                    'WIDTH': '392',
                    'HEIGHT': '30',
                    'VALIGN': 'MIDDLE'
                },
                'tag_attr_matched_len': 2,
                'string_list': [],
                'parent_tag_name': 'TR',
                'parent_tag_attr_dict': {'ACOPY': 'N', 'ADELETE': 'N'},
                'sibling_before_tag_name': 'TD',
                'sibling_before_tag_attr_dict': {'WIDTH': '108', 'HEIGHT': '30', 'VALIGN': 'MIDDLE', 'ALIGN': 'CENTER', 'AUPDATECONT': 'N'},
                'sibling_before_tag_string': '(도로명주소)',
                'sibling_next_tag_name': '',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['감사보고서', '연결감사보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 33,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'INSERTION',
                'sibling_before_tag_attr_dict': {'ABASISNUMBER': 'SE1', 'ADUPLICATION': 'N', 'AFREQUENCY': '0'},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['반기감사보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 24,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'WARNING',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '※IFRS적용기업의경우:&cr;편집기상단메뉴중[도구=>문서헤더정보입력=>추가정보부분의IFRS적용유무]를설정후,&cr;표를직접만들어사용하시기바랍니다.',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['분기감사보고서', '분기연결감사보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 24,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'PGBRK',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['반기연결감사보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 24,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'PGBRK',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['반기연결검토보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 32,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'PGBRK',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['분기연결검토보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 32,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'PGBRK',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FS
            {
                'variable_name': '###FS',
                'target_dsd_name': ['반기검토보고서', '분기검토보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 32,
                'string_list': [],
                'parent_tag_name': 'SECTION-1',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY', 'APARTSOURCE': 'SOURCE'},
                'sibling_before_tag_name': 'WARNING',
                'sibling_before_tag_attr_dict': {},
                'sibling_before_tag_string': '※IFRS적용기업의경우:&cr;편집기상단메뉴중[도구=>문서헤더정보입력=>추가정보부분의IFRS적용유무]를설정후,&cr;표를직접만들어사용하시기바랍니다.',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },

            # ###FN
            {
                'variable_name': '###FN',
                'target_dsd_name': ['감사보고서', '연결감사보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 33,
                'string_list': [],
                'parent_tag_name': 'SECTION-2',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY'},
                'sibling_before_tag_name': 'TABLE',
                'sibling_before_tag_attr_dict': {'ACLASS': 'NORMAL', 'AFIXTABLE': 'N', 'WIDTH': '600', 'BORDER': '0'},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FN
            {
                'variable_name': '###FN',
                'target_dsd_name': ['반기감사보고서', '반기연결감사보고서', '분기감사보고서', '분기연결감사보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 24,
                'string_list': [],
                'parent_tag_name': 'SECTION-2',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY'},
                'sibling_before_tag_name': 'TABLE',
                'sibling_before_tag_attr_dict': {'ACLASS': 'NORMAL', 'AFIXTABLE': 'N', 'WIDTH': '600', 'BORDER': '0'},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            },
            # ###FN
            {
                'variable_name': '###FN',
                'target_dsd_name': ['반기검토보고서', '반기연결검토보고서', '분기검토보고서', '분기연결검토보고서'],
                'tag_name': 'P',
                'attr_dict': {},
                'tag_attr_matched_len': 32,
                'string_list': [],
                'parent_tag_name': 'SECTION-2',
                'parent_tag_attr_dict': {'ACLASS': 'MANDATORY'},
                'sibling_before_tag_name': 'TABLE',
                'sibling_before_tag_attr_dict': {'ACLASS': 'NORMAL', 'AFIXTABLE': 'N', 'WIDTH': '600', 'BORDER': '0'},
                'sibling_before_tag_string': '',
                'sibling_next_tag_name': 'P',
                'sibling_next_tag_attr_dict': {},
                'sibling_next_tag_string': '',
                'matched_len': 1
            }
        ]

        # DSD 마다 ### 변수 위치 확인
        for dsd_name in self.dsd_name_list:
            dsd_file_list = self.open_dsd_file(mode='original', dsd_name=dsd_name)

            # contents 파일 선택
            contents_file_row = [row for row in dsd_file_list if row['name'].find('contents') != -1]
            if len(contents_file_row) == 1:
                print('got contents.xml')
                contents_file_row = contents_file_row[0]
            else:
                print('ERR: multiple contents.xml file')
                raise

            soup = contents_file_row['data_bs']

            # ### 변수 별로 위치 특정되는지 확인
            for tag_location_row in tag_location_descriptions:

                variable_name = tag_location_row['variable_name']
                target_dsd_name = tag_location_row['target_dsd_name']
                tag_name = tag_location_row['tag_name']
                attr_dict = tag_location_row['attr_dict']
                tag_attr_matched_len = tag_location_row['tag_attr_matched_len']
                string_list = tag_location_row['string_list']
                parent_tag_name = tag_location_row['parent_tag_name']
                parent_tag_attr_dict = tag_location_row['parent_tag_attr_dict']
                sibling_before_tag_name = tag_location_row['sibling_before_tag_name']
                sibling_before_tag_attr_dict = tag_location_row['sibling_before_tag_attr_dict']
                sibling_before_tag_string = tag_location_row['sibling_before_tag_string']
                sibling_next_tag_name = tag_location_row['sibling_next_tag_name']
                sibling_next_tag_attr_dict = tag_location_row['sibling_next_tag_attr_dict']
                sibling_next_tag_string = tag_location_row['sibling_next_tag_string']
                matched_len = tag_location_row['matched_len']

                if dsd_name in target_dsd_name:

                    # filter 1-1: tag.name 과 tag.attrs 로 filtering
                    tag_found = soup.find_all(tag_name, attr_dict)
                    if len(tag_found) == tag_attr_matched_len:
                        print(variable_name, 'tag_attr_matched_len correct', tag_attr_matched_len)

                        # filter 1-2: tag.string 으로 filtering
                        tag_found_filtered = []
                        for index_tag, tag in enumerate(tag_found):
                            if tag.string:
                                tag_found_string = tag.string.strip().replace(' ', '')
                            else:
                                tag_found_string = ''

                            if len(string_list):
                                tag_string = [row['string_alpha'] for row in string_list if row['dsd_name'] == dsd_name][0]
                            else:
                                tag_string = ''

                            if tag_found_string == tag_string:
                                print(index_tag, 'tag_string matched')
                                tag_found_filtered.append(tag)
                            else:
                                print(index_tag, 'tag_string unmatched', tag_found_string, tag_string)
                    else:
                        print(f'{variable_name} ERR: tag_attr_matched_len not matched', len(tag_found), tag_attr_matched_len, tag_found)
                        raise

                    # filter 2: parent, siblings .name 과 .attrs 로 filtering
                    tag_founded = []

                    for index_tag, tag in enumerate(tag_found_filtered):

                        parent_tag_found = tag.parent
                        parent_tag_found_name = parent_tag_found.name
                        parent_tag_found_attrs = parent_tag_found.attrs

                        # filter 2-1: parent.name 과 parent.attrs 로 filtering
                        if parent_tag_found_name == parent_tag_name and parent_tag_found_attrs == parent_tag_attr_dict:
                            print(index_tag, 'parent_tag matched')

                            if sibling_before_tag_name:
                                flag_sibling_before = False
                            else:
                                flag_sibling_before = True
                                print(index_tag, 'sibling_before_tag matched')

                            if sibling_next_tag_name:
                                flag_sibling_next = False
                            else:
                                flag_sibling_next = True
                                print(index_tag, 'sibling_next_tag matched')

                            # filter 2-2: sibling_before.name 과 sibling_before.attrs 로 filtering
                            if not flag_sibling_before:
                                for s in tag.previous_siblings:

                                    if isinstance(s, bs4.element.Tag):
                                        sibling_before_tag_found = s
                                        sibling_before_tag_found_name = sibling_before_tag_found.name
                                        sibling_before_tag_found_attrs = sibling_before_tag_found.attrs
                                        if sibling_before_tag_found.string:
                                            sibling_before_tag_found_string = sibling_before_tag_found.string.strip().replace(' ', '')
                                        else:
                                            sibling_before_tag_found_string = ''

                                        if sibling_before_tag_found_name == sibling_before_tag_name and \
                                                sibling_before_tag_found_attrs == sibling_before_tag_attr_dict and \
                                                sibling_before_tag_found_string == sibling_before_tag_string:
                                            print(index_tag, 'sibling_before_tag matched')
                                            flag_sibling_before = True

                                        else:
                                            print(index_tag, 'sibling_before_tag unmatched', sibling_before_tag_found_name, sibling_before_tag_found_attrs, sibling_before_tag_found_string)
                                        break

                            # filter 2-3: sibling_next.name 과 sibling_next.attrs 로 filtering
                            if not flag_sibling_next:
                                for s in tag.next_siblings:
                                    if isinstance(s, bs4.element.Tag):
                                        sibling_next_tag_found = s
                                        sibling_next_tag_found_name = sibling_next_tag_found.name
                                        sibling_next_tag_found_attrs = sibling_next_tag_found.attrs
                                        if sibling_next_tag_found.string:
                                            sibling_next_tag_found_string = sibling_next_tag_found.string.strip().replace(' ', '')
                                        else:
                                            sibling_next_tag_found_string = ''

                                        if sibling_next_tag_found_name == sibling_next_tag_name and \
                                                sibling_next_tag_found_attrs == sibling_next_tag_attr_dict and \
                                                sibling_next_tag_found_string == sibling_next_tag_string:
                                            print(index_tag, 'sibling_next_tag matched')
                                            flag_sibling_next = True
                                        else:
                                            print(index_tag, 'sibling_next_tag unmatched',sibling_next_tag_found_name, sibling_next_tag_found_attrs, sibling_next_tag_found_string)
                                        break

                            if flag_sibling_before and flag_sibling_next:
                                print(index_tag, 'FOUND filtered tag')
                                tag_founded.append(tag)

                        else:
                            print(index_tag, 'parent_tag unmatched', parent_tag_found_name, parent_tag_found_attrs)

                    if len(tag_founded) == matched_len:
                        print(variable_name, 'tag founded')
                        for tag in tag_founded:
                            tag.string = variable_name

                    else:
                        print('ERR: non-matched founded', tag_founded, sep='\n')
                        raise

                else:
                    print(variable_name, 'is not for', dsd_name)

            data_contents = str(contents_file_row['data_bs'])
            data_meta = str([row for row in dsd_file_list if row['name'].find('meta') != -1][0]['data_bs'])
            self.make_dsd_file(
                f'{self.path_default}/with_triple_sharp',
                f'{dsd_name}.dsd',
                data_contents,
                data_meta
            )

    def make_dsd_file(self, path_dir, file_name, data_contents, data_meta):

        with zipfile.ZipFile(f'{path_dir}/{file_name}', mode='w', compression=zipfile.ZIP_DEFLATED) as f:
            f.writestr(data=data_contents, zinfo_or_arcname='contents.xml')
            f.writestr(data=data_meta, zinfo_or_arcname='meta.xml')
            f.close()

        print('finished')


if __name__ == '__main__':

    DSDHandler = DSDHandler()
    # file_list = DSDHandler.open_dsd_file(mode='original', dsd_name='감사보고서')
    # for file in file_list:
    #     print(file)
    DSDHandler.make_triple_sharp_dsd()
