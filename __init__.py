from typing import Union
from dataclasses import dataclass
from utils import *
import pathlib
import _io
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


@dataclass
class Style:
    Name = 'Default'
    FontName = 'Arial'
    Fontsize = 10
    # TODO: more another default value
    UnknownFormat = {}

    def __init__(self, style_content, style_formats):
        for style_format, style in zip(style_formats, style_content):
            if style_format not in StyleFormats:
                self.UnknownFormat[style_format] = style
                continue

            # TODO: parse format value
            if style_format in []:
                style = int(style)
            elif style_format in []:
                style = bool(style)
            setattr(self, style_format, style)


class ASS:
    ScriptType = 'v4.00+'
    WrapStyle = 0
    ScaledBorderAndShadow = True
    YCbCrMatrix = None
    PlayResX = 1920
    PlayResY = 1080
    Information = ScriptInformation
    UnknownScriptInfo = {}

    Styles = {}

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

        for line in iter(ass_lines):
            section_name = re.findall(r'^\s*\[\s*(.*)\s*]\s*$', line)
            if section_name:
                section_name = section_name[0]
                break
        else:
            return

        while True:
            if section_name == 'Script Info':
                parser = self.__script_info_parser
            elif re.match(r'V4\+? Styles', section_name):
                self.__format = StyleFormats
                parser = self.__styles_parser
            elif section_name == 'Events':
                self.__format = EventFormats
                parser = self.__events_parser
            elif section_name == 'Fonts':
                parser = self.__fonts_parser
            else:
                parser = self.__unknown_parser

            section_name = self.__parse_section(parser, ass_lines)

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
        header, value = re.split(r'\s*:\s*', ass_line, maxsplit=1)
        value = re.findall(r'\s*([^,]+)\s*', value)
        if header == 'Format':
            self.__format = value
        elif header == 'Style':
            style = Style(value, self.__format)
            self.Styles[style.Name] = style

    def __events_parser(self, ass_line: str):
        pass  # TODO

    def __fonts_parser(self, ass_line: str):
        pass  # TODO

    def __unknown_parser(self, ass_line: str):
        pass  # TODO


if __name__ == '__main__':
    ass_parser = ASS(r'./test/test.ass')
    pass
