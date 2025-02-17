from typing import Union
from dataclasses import dataclass
from utils import *
import pathlib
import _io
import os.path
import re


@dataclass
class ScriptInformation:
    Title = None
    OriginalScript = None
    OriginalTranslation = None
    OriginalEditing = None
    OriginalTiming = None
    ScriptUpdatedBy = None
    UpdateDetails = None


class ASS:
    ScriptType = 'v4.00+'
    WrapStyle = 0
    ScaledBorderAndShadow = True
    YCbCrMatrix = None
    PlayResX = 1920
    PlayResY = 1080
    Information = ScriptInformation
    UnknownScriptInfo = {}

    def __init__(
            self,
            ass: Union[str, pathlib.Path, _io.TextIOWrapper],
            encoding: str = 'utf-8-sig'
    ):
        if isinstance(ass, str):
            if re.match(r'^(?:(?:[a-zA-Z]:|\.{1,2})?[\\/](?:[^\\?/*|<>:"]+[\\/])*)'
                        r'(?:(?:[^\\?/*|<>:"]+?)(?:\.[^.\\?/*|<>:"]+)?)?$', ass):
                ass = pathlib.Path(ass)
            else:
                ass_content = ass
        if isinstance(ass, pathlib.Path):
            ass = open(ass, 'r', encoding=encoding)
        if isinstance(ass, _io.TextIOWrapper):
            ass_content = ass.read()
            ass.close()
        ass_lines = iter(re.split(r'\r?\n', ass_content))

        section_name = None
        for line in iter(ass_lines):
            if section_name:
                section_name = section_name[0]
                if section_name == 'Script Info':
                    section_name = self.__parse_section(self.__script_info_parser, ass_lines)
                elif re.match(r'V4\+? Styles', section_name):
                    section_name = self.__parse_section(self.__styles_parser, ass_lines)
                elif section_name == 'Events':
                    section_name = self.__parse_section(self.__events_parser, ass_lines)
                elif section_name == 'Fonts':
                    section_name = self.__parse_section(self.__fonts_parser, ass_lines)
                else:
                    section_name = self.__parse_section(self.__nonstandard_parser, ass_lines)

            else:
                section_name = re.findall(r'^\s*\[\s*(.*)\s*]\s*$', line)

    @staticmethod
    def __parse_section(parser, ass_lines: iter):
        for line in ass_lines:
            line = re.sub(r'^\s*|\s*$', '', line)
            if not line or re.match(r'^[;|!]', line):
                continue
            section_name = re.findall(r'^\[\s*(.*)\s*]$', line)
            if section_name:
                return section_name[0]
            parser(line)
        return None

    def __script_info_parser(self, ass_line: str):
        header, value = re.split(r'\s*:\s*', ass_line, maxsplit=1)
        if header == 'WrapStyle':
            self.wrapStyle = int(value)
        elif header == 'ScaledBorderAndShadow':
            self.scaledBorderAndShadow = False if value == 'no' else True
        elif header in ['ScriptType', 'YCbCr Matrix']:
            setattr(self, header, value)
        elif header in ['LayoutResX', 'LayoutResY', 'PlayResX', 'PlayResY']:
            setattr(self, header, int(value))
        elif header in InformationHeaders:
            setattr(self.Information, re.sub(r'\s', '', header), value)

    def __styles_parser(self, ass_line: str):
        pass  # TODO

    def __events_parser(self, ass_line: str):
        pass  # TODO

    def __fonts_parser(self, ass_line: str):
        pass  # TODO

    def __nonstandard_parser(self, ass_line: str):
        pass  # TODO


if __name__ == '__main__':
    ass_parser = ASS(r'./test/test.ass')
    pass
