from typing import Union, Optional
from dataclasses import dataclass
from utils import *
import pathlib
import _io
import re


@dataclass
class ScriptInformation:
    Title: str = None
    OriginalScript: str = None
    OriginalTranslation: str = None
    OriginalEditing: str = None
    OriginalTiming: str = None
    ScriptUpdatedBy: str = None
    UpdateDetails: str = None


@dataclass
class Colour:
    R: int = 255
    G: int = 255
    B: int = 255
    Alpha: float = 1

    def __init__(
            self, *args,
            colourcode: Optional[str] = None,
            r: Optional[int] = None,
            g: Optional[int] = None,
            b: Optional[int] = None,
            alpha: Optional[float] = 1
    ):
        if colourcode is not None:
            colour = self._parse_colourcode(colourcode)
        elif r is not None and g is not None and b is not None:
            colour = (alpha, r, g, b)
        else:
            colour = []
            for arg in args:
                if isinstance(arg, str):
                    colour = self._parse_colourcode(arg)
                    break
                elif isinstance(arg, int):
                    colour.append(arg)
            else:
                if len(colour) == 3:
                    colour.insert(0, 1)
                elif len(colour) >= 4:
                    colour = [colour[1:5]].append(colour[0])
                else:
                    colour = (self.Alpha, self.R, self.G, self.B)
        self.Alpha, self.R, self.G, self.B = colour

    def _parse_colourcode(self, colourcode: Optional[str] = ''):
        primary_colours = re.findall(r'^&?H?([0-9A-F]{2}){3,4}&?$', colourcode)  # TODO: need to check
        colours = [self.Alpha, self.R, self.G, self.B]
        if len(primary_colours) == 4:
            colours[0] = int(primary_colours.pop(0), 16) / 255
        if len(primary_colours) == 3:
            colours[1], colours[2], colours[3] = [int(primary_colour, 16) for primary_colour in primary_colours]
        return tuple(colours)


@dataclass
class Style:
    Name: str = 'Default',
    Fontname: str = 'Arial',
    Fontsize: int = 20,
    PrimaryColour: Colour = Colour(),
    SecondaryColour: Colour = Colour(),
    OutlineColour: Colour = Colour(),
    BackColour: Colour = Colour(),
    Bold: bool = False,
    Italic: bool = False
    Underline: bool = False
    StrikeOut: bool = False
    ScaleX: float = 100.
    ScaleY: float = 100.
    Spacing: float = 0.
    Angle: float = 0.
    BorderStyle: int = 1
    Outline: float = 2.
    Shadow: float = 2.
    Alignment: int = 2
    MarginL: int = 10
    MarginR: int = 10
    MarginV: int = 10
    Encoding: int = 1
    UnknownFormat = dict()

    def __init__(self, style_content, style_formats):
        for style_format, style in zip(style_formats, style_content):
            if style_format not in StyleFormats:
                self.UnknownFormat[style_format] = style
                continue

            if (
                    style_format == StyleFormats[16] or
                    style_format in StyleFormats[18:]
            ):
                style = int(style)
            elif (
                    style_format == StyleFormats[2] or
                    style_format in StyleFormats[11: 15] or
                    style_format in StyleFormats[16: 18]
            ):
                style = float(style)
            elif style_format in StyleFormats[7: 11]:
                style = bool(style)
            elif style_format in StyleFormats[3: 7]:
                style = Colour(style)
            setattr(self, style_format, style)


class ASS:
    ScriptType: str = 'v4.00+'
    WrapStyle: int = 0
    ScaledBorderAndShadow: bool = True
    YCbCrMatrix: str = None
    PlayResX: int = 1920
    PlayResY: int = 1080
    Information: ScriptInformation = ScriptInformation()
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
