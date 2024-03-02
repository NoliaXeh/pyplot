# This file contains the Plot class, which is the main class of the library.

from dataclasses import dataclass
import re
import json

class PlotError(Exception):
    def __init__(self, message, char_number: int = None, line = None):  
        self.message = message
        self.char_number = char_number
        self.line = line

    @property
    def details(self):
        if self.char_number is None:
            return f"Error: {self.message}"
        return \
        f"Error: {self.message} at char {self.char_number}:\n" + \
        f"{self.line!r}\n" + \
        f"{' ' * self.char_number}^"

    def __str__(self):
        return self.details

class Plot:
    """
    A class to represent a plot.
    A plot is a visual representation of a scenario, resembling a sequence diagram.
    """

    def __init__(self, title: str, filename: str):
        self.title = title
        self.filename = filename
        self.actors = []
        self.messages = []
        self.parser = PlotParser(filename, self)

    def parse(self):
        self.parser.parse()

@dataclass
class Actor:
    name: str
    column: int
    data: dict[str, str] = None

    def __str__(self):
        return f'{self.name}({self.column})'

@dataclass
class Message:
    sender: str
    receiver: str
    bydirectional: bool
    content: str
    line: int
    order: int = 0
    title: str = None
    data: dict[str, str] = None

    def __str__(self):
        direction = '<->' if self.bydirectional else '-->'
        return f"[{self.order}] {self.sender}\t{direction}\t{self.receiver}\t: {self.content!r}"

    def __repr__(self):
        return self.__str__().replace('\t', ' ')

class PlotParser:
    def __init__(self, filename: str, plot: Plot):
        self.filename = filename
        with open(filename, 'r') as file:
            self.data = file.read().split("\n")
        self.plot = plot

    def parse(self):
        # Parse the actors. They are the first line of the file, speparated by multiple spaces.
        actors = self.data[0].split(" ")
        regex_actors = re.compile(r"[A-Za-z0-9_-]+")
        actors = regex_actors.findall(self.data[0])
        self.plot.actors = [Actor(actor, index) for index, actor in enumerate(actors)]
        # Parse the messages. They are the rest of the file.
        for line_no, line in enumerate(self.data[1:]):
            try:
                self.parse_line(line, line_no)
            except PlotError as e:
                print(f"Error parsing file {self.filename}, line {line_no + 2}")
                print(e.details)
                raise e
            except Exception as e:
                print(f"Error parsing file {self.filename} : {line_no + 2}")
                print(f"Invalid syntax:\n\t`{line}`")
                raise e

        for message in self.plot.messages:
            # extract the json data from the message content, if any
            if '{' not in message.content:
                title = message.content.strip().split(' ')[0] if ' ' in message.content else message.content
                message.title = title
                message.content = message.content.strip()[len(title):].strip()
                message.data = {}
                continue
            if '}' not in message.content:
                raise PlotError("invalid json data, no ending }", char_number=len(message.content), line=message.content)
            json_start = message.content.find('{')
            json_end = message.content.find('}')
            json_raw = message.content[json_start:json_end + 3]
            try:
                message.data = json.loads(json_raw)
            except json.JSONDecodeError as e:
                raise PlotError(f"invalid json data for message line line {message.line}: \n {e.msg}", char_number=json_start, line=json_raw)
            message.title = message.content[:json_start].strip()
        return self.plot

    def parse_line(self, line: str, line_no: int):
        # Parse the line and add its message to the plot.
        regex_line_is_new_message = re.compile(r"\|.*-.*\|.*")
        if not re.match(regex_line_is_new_message, line) and self.plot.messages:
            cnt = 0
            for i, char in enumerate(line):
                if char == '|':
                    cnt += 1
                if cnt == len(self.plot.actors):
                    break
            data = line[i + 1:]
            if data and data[0] == ' ':
                data = data[1:]
            if data and data[0] == '#':
                return
            if not data:
                return
            self.plot.messages[-1].content += '\n' + data
            return
        nb_columns_befor_message = -1
        nb_columns_after_message = 0
        message_found = False
        arrow_ended = False
        message_direction = ''
        end_of_columns = -1
        for i, char in enumerate(line):
            if message_found and char == '|':
                nb_columns_after_message += 1
            elif char == '|':
                nb_columns_befor_message += 1
            elif char == '-':
                if arrow_ended:
                    raise PlotError("multiple arrows in the same line", char_number=i, line=line)
                message_found = True
            elif char == '>':
                message_direction += '>'
            elif char == '<':
                message_direction += '<'
            elif char not in '\t -|<>':
                end_of_columns = i - 1
                break
            if message_found and char != '-':
                arrow_ended = True
        else:
            end_of_columns = len(line) - 1
        if not message_found:
            return
        # data is after the last '|'
        if nb_columns_after_message > 0:
            data = line[end_of_columns + 1:]

        if not data:
            raise PlotError("no message content. If you want no operation, use `#` to indicate it wasn't a mistake.", char_number=end_of_columns, line=line)

        index_left_actor = nb_columns_befor_message
        index_right_actor = len(self.plot.actors) - nb_columns_after_message

        left = self.plot.actors[index_left_actor]
        right = self.plot.actors[index_right_actor]
        order = len(self.plot.messages)
        if message_direction in ('<>', '><'):
            sender = left
            receiver = right
            bydirectional = True
        elif message_direction == '>':
            sender = left
            receiver = right
            bydirectional = False
        elif message_direction == '<':
            sender = right
            receiver = left
            bydirectional = False
        else:
            sender = left
            receiver = right
            bydirectional = True

        message = Message(sender=sender, receiver=receiver, bydirectional=bydirectional, content=data, order=order, line=line_no+2)
        self.plot.messages.append(message)