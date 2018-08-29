"""Converter from flake8 output to checkstyle xml."""

import logging
import re

from argparse import ArgumentParser
from xml.etree import ElementTree


class Converter(object):

    XML_HEADER = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
    CHECKSTYLE_HEADER = '<checkstyle version="4.3">'
    CHECKSTYLE_FOOTER = '</checkstyle>'

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.regexp = re.compile('.* ([^:]*):(\d+):(\d+): ([^ ]*) (.*)')
        self.last_file = ''
        self.root = None

    def line_generator(self):
        try:
            with open(self.input_file, 'r') as src:
                for line in src:
                    yield line
        except IOError as ex:
            logging.error(ex)

    def get_severity(self, code):
        if code[0] in ('E',):
            return 'error'
        return 'warning'

    def process_message(self, out, file_path, line, column, code, message):
        if self.last_file != file_path:
            if self.last_file:
                out.write(ElementTree.tostring(self.root))
            self.last_file = file_path
            self.root = ElementTree.Element('file', {
                'name': file_path
            })
        ElementTree.SubElement(self.root, 'error', {
            'line': line,
            'column': column,
            'severity': self.get_severity(code),
            'message': message,
            'source': 'flake8.{}'.format(code)
        })

    def convert(self):
        try:
            with open(self.output_file, 'w') as out:
                out.write(self.XML_HEADER)
                out.write(self.CHECKSTYLE_HEADER)
                for line in self.line_generator():
                    match = self.regexp.match(line)
                    if match:
                        self.process_message(
                            out,
                            match.group(1),
                            match.group(2),
                            match.group(3),
                            match.group(4),
                            match.group(5))
                out.write(self.CHECKSTYLE_FOOTER)
        except Exception as ex:
            logging.error(ex)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', required=True, help="input file")
    parser.add_argument('-o', '--output', dest='output', required=True, help="output file")
    args = parser.parse_args()
    conv = Converter(args.input, args.output)
    conv.convert()
