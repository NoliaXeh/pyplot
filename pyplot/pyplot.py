# This file contains the Plot class, which is the main class of the library.

from dataclasses import dataclass
import re

class PlotError(Exception):
    def __init__(self, message):
        self.message = message

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
    order: int = 0

    def __str__(self):
        direction = '<->' if self.bydirectional else '-->'
        return f"[{self.order}] {self.sender}\t{direction}\t{self.receiver}\t: {self.content}"

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
                self.parse_line(line)

            except PlotError as e:
                print(f"Error parsing file {self.filename} : {line_no + 2}")
                print(e.message)
                print(line)
                raise e
            except Exception as e:
                print(f"Error parsing file {self.filename} : {line_no + 2}")
                print(f"Invalid syntax:\n\t`{line}`")
        print(*self.plot.messages, sep='\n')
        return self.plot

    def parse_line(self, line: str):
        # Parse the line and add its message to the plot.
        if '-' not in line:
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
                    raise PlotError("Error: multiple arrows in the same line")
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

        index_left_actor = nb_columns_befor_message
        index_right_actor = len(self.plot.actors) - nb_columns_after_message

        left = self.plot.actors[index_left_actor]
        right = self.plot.actors[index_right_actor]
        order = len(self.plot.messages)
        if message_direction in ('<>', '><'):
            message = Message(left, right, True, data, order)
        elif message_direction == '>':
            message = Message(left, right, False, data, order)
        elif message_direction == '<':
            message = Message(right, left, False, data, order)
        else:
            message = Message(left, right, True, data, order)

        self.plot.messages.append(message)