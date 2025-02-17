from typing import Union
import pathlib
import _io
import os.path
import re


class ASS:
    def __init__(
            self,
            ass: Union[str, pathlib.Path, _io.TextIOWrapper],
            encoding: str = 'utf-8-sig'
    ):
        if isinstance(ass, str):
            if os.path.exists(ass):
                ass = pathlib.Path(ass)
            else:
                ass_content = ass
        if isinstance(ass, pathlib.Path):
            ass = open(ass, 'r', encoding=encoding)
        if isinstance(ass, _io.TextIOWrapper):
            ass_content = ass.read()
            ass.close()
        ass_lines = iter(re.split(r'\r?\n', ass_content))

        # for line in iter(re.split(r'\r?\n', ass_content)):
        #     line = line.strip()
        #     section_name = re.findall(r'^\[(.*)]$', line)
        #     if section_name:
        #         section_name = section_name[0]
        #         continue

        section_name = None
        for line in iter(re.split(r'\r?\n', ass_lines)):
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
        self.__setattr__(header, value)

    def __styles_parser(self, ass_line: str):
        pass  # TODO

    def __events_parser(self, ass_line: str):
        pass  # TODO

    def __fonts_parser(self, ass_line: str):
        pass  # TODO

    def __nonstandard_parser(self, ass_line: str):
        pass  # TODO


if __name__ == '__main__':
    ass_parser = ASS(r'../test.ass')
    print()
