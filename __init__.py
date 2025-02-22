from typing import Union, Optional, List, Tuple, Callable, Any
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
        if colourcode:
            colour = self.parse_colourcode(colourcode)
            if not colour:
                return
        elif r and g and b:
            colour = (alpha, r, g, b)
        else:
            colour = list()
            for arg in args:
                if isinstance(arg, str):
                    colour = self.parse_colourcode(arg)
                    if not colour:
                        return
                    break
                elif isinstance(arg, int):
                    colour.append(arg)
            else:
                if len(colour) == 3:
                    colour.insert(0, 1)
                elif len(colour) >= 4:
                    colour = [colour[4]].extend(colour[:4])
                else:
                    return
        self.Alpha, self.R, self.G, self.B = colour

    @staticmethod
    def parse_colourcode(colourcode: str) -> Optional[tuple]:
        primary_colours = re.findall(r'^&?H?((?:[0-9A-F]{2}){3,4})&?$', colourcode)
        if not primary_colours:
            return None
        primary_colours = list(primary_colours[0])
        alpha = 1 if len(primary_colours) == 6 else int(primary_colours.pop(0) + primary_colours.pop(0), 16) / 255
        colours = [alpha, ]
        for i in range(3):
            colours.append(int(primary_colours.pop(0) + primary_colours.pop(0), 16))
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

    def __init__(
            self,
            style_content: Optional[str] = None,
            style_formats: Optional[Union[List[str], Tuple[str]]] = None
    ):
        if not (style_content and style_formats):
            return
        style_content = re.findall(r'\s*([^,]+)\s*', style_content)
        for style, style_format in zip(style_content, style_formats):
            if style_format not in StyleFormats:
                self.UnknownFormat[style_format] = style
                continue

            if (
                    style_format == StyleFormats[15] or
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


@dataclass
class TimeSegment:
    Start: float = 0.
    End: float = 0.

    def __init__(
            self, *args,
            timecodes: Optional[Union[List[str], Tuple[str]]] = None,
            start: Optional[Union[int, float]] = None,
            end: Optional[Union[int, float]] = None
    ):
        if timecodes:
            time_segment = self.parse_timecode(timecodes)
            if not time_segment:
                return
        elif start and end:
            time_segment = (float(start), float(end))
        else:
            time_segment = list()
            for arg in args:
                if isinstance(arg, (list, tuple)):
                    time_segment = self.parse_timecode(arg)
                    if not time_segment:
                        return
                    break
                elif isinstance(arg, (int, float)):
                    time_segment.append(float(arg))
                    if len(time_segment) == 2:
                        break
            else:
                return
        self.Start, self.End = time_segment

    @property
    def Duration(self) -> float:
        return self.End - self.Start

    @staticmethod
    def parse_timecode(timecodes: Union[List[str], Tuple[str]]) -> Optional[tuple]:
        time_segment = list()
        for timecode in timecodes:
            time_info = re.findall(r'^(\d):(\d\d):(\d\d).(\d\d)$', timecode)
            if not time_info:
                return None
            hours, minutes, seconds, millie_seconds = time_info[0]
            time_segment.append(
                float(3600 * int(hours) + 60 * int(minutes) + int(seconds) + 0.01 * int(millie_seconds)))
        return tuple(time_segment)


class Text:
    def __init__(self, text: Optional[str] = ''):
        pass  # TODO


@dataclass
class __Event:
    Layer: int = 0
    TimeSegment: TimeSegment = TimeSegment()
    Style: str = 'Default'
    Name: str = ''
    MarginL: int = 0
    MarginR: int = 0
    MarginV: int = 0
    Effect: str = ''
    Text: Text = Text()

    UnknownFormat = dict()

    def __init__(
            self,
            event_content: Optional[str] = None,
            event_formats: Optional[Union[List[str], Tuple[str]]] = None
    ):
        if not (event_content and event_formats):
            return
        event_content = re.split(r',', event_content, maxsplit=len(event_formats) - 1)
        time_segment = dict()
        for event, event_format in zip(event_content, event_formats):
            if event_format not in EventFormats:
                self.UnknownFormat[event_format] = event
                continue
            if event_format == EventFormats[9]:
                event = Text(event)
            else:
                event = re.sub(r'^\s*|\s*$', '', event)
            if (
                    event_format == EventFormats[0] or
                    event_format in EventFormats[5: 8]
            ):
                event = int(event)
            elif event_format in EventFormats[1: 3]:
                time_segment[event_format] = event
                continue
            setattr(self, event_format, event)
        if 'Start' in time_segment.keys() and 'End' in time_segment.keys():
            self.TimeSegment = TimeSegment([time_segment['Start'], time_segment['End']])


class Dialogue(__Event):
    pass


class Comment(__Event):
    pass


class ASS:
    ScriptType: str = 'v4.00+'
    WrapStyle: int = 0
    ScaledBorderAndShadow: bool = True
    YCbCrMatrix: str = None
    PlayResX: int = 1920
    PlayResY: int = 1080
    Information: ScriptInformation = ScriptInformation()
    UnknownScriptInfo = dict()

    Styles = {'Default': Style()}
    Events = list()

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
                self.format = StyleFormats
                parser = self.__styles_parser
            elif section_name == 'Events':
                self.format = EventFormats
                parser = self.__events_parser
            elif section_name == 'Fonts':
                parser = self.__fonts_parser
            else:
                parser = self.__unknown_parser

            section_name = self.__parse_section(parser, ass_lines)
            if not section_name:
                if hasattr(self, 'format'):
                    delattr(self, 'format')
                break

    @staticmethod
    def __parse_section(parser: Callable[[str], Any], ass_lines: iter) -> Optional[str]:
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
        if header == 'Format':
            self.format = re.findall(r'\s*([^,]+)\s*', value)
        elif header == 'Style':
            style = Style(value, self.format)
            self.Styles[style.Name] = style

    def __events_parser(self, ass_line: str):
        header, value = re.split(r'\s*:\s*', ass_line, maxsplit=1)
        if header == 'Format':
            self.format = re.findall(r'\s*([^,]+)\s*', value)
        elif header == 'Dialogue':
            self.Events.append(Dialogue(value, self.format))
        elif header == 'Comment':
            self.Events.append(Comment(value, self.format))

    def __fonts_parser(self, ass_line: str):
        pass  # TODO

    def __unknown_parser(self, ass_line: str):
        pass  # TODO


if __name__ == '__main__':
    ass_parser = ASS(r'./test/test.ass')
    pass
