# This file contains the Plot class, which is the main class of the library.

from dataclasses import dataclass
import re
import json

class PlotError(Exception):
    """
    Custom exception class for plotting errors.
    """

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

    Attributes:
        title (str): The title of the plot.
        filename (str): The filename of the plot.
        actors (list): A list of actors in the plot.
        messages (list): A list of messages in the plot.
        parser (PlotParser): The parser used to parse the plot file.

    Methods:
        __init__(self, title: str, filename: str): Initializes a new Plot object.
        parse(self): Parses the plot file using the parser.
    """
    __id = 0
    def __init__(self, title: str, filename: str):
        self.title = title
        self.filename = filename
        self.actors = []
        self.messages = []
        self.parser = PlotParser(filename, self)
        self.id = Plot.__id
        Plot.__id += 1

    def parse(self):
        self.parser.parse()

    def set_actor_data(self, data: dict[str, str], actor_name: str) -> bool:
        """
        Sets the data for an actor in the plot.

        Args:
            data (dict[str, str]): The data to be set.
            actor_name (str): The name of the actor.

        Returns:
            bool: True if the actor was found and the data was set, False otherwise.
        """
        for actor in self.actors:
            if actor.name == actor_name:
                actor.data = data
                return True
        return False

    def export(self) -> str:
        lines = []
        actor_max_width = max([len(actor.name) for actor in self.actors])
        column_width = max(actor_max_width, 15)
        head = (' ' * (max(column_width - actor_max_width, 1))).join([actor.name for actor in self.actors])
        lines.append(head)
        arrow_right = '-' * (column_width - 1) + '>'
        arrow_left = '<' + '-' * (column_width - 1)
        arrow_both = '<' + '-' * (column_width - 2) + '>'
        arrow_blank = ' ' * column_width
        arrow_line = '-' * column_width
        empty_line = ('|' + arrow_blank) * (len(self.actors) - 1) + '|'
        lines.append(empty_line)
        for message in self.messages:
            message: Message
            sender_col = message.sender.column
            receiver_col = message.receiver.column
            left = min(sender_col, receiver_col)
            right = max(sender_col, receiver_col)
            line = ''
            for afrom, ato in zip(self.actors, self.actors[1:]):
                afrom : Actor
                ato : Actor
                if afrom.column == left and ato.column == right:
                    line += '|' + arrow_both
                elif afrom.column == left:
                    line += '|' + arrow_left
                elif ato.column == right:
                    line += '-' + arrow_right
                elif afrom.column > left and ato.column < right:
                    line += '-' + arrow_line
                else:
                    line += '|' + arrow_blank
            line += '|'
            if not message.bydirectional:
                to_replace = '<' if (message.sender.column < message.receiver.column) else '>'
                line = line.replace(to_replace, '-')
            line += ' '
            if message.data:
                line += message.title + ' ' + json.dumps(message.data, indent=4)
            else:
                line += message.title + ' ' + message.content
            line = line.replace('\n', '\n' + empty_line + ' ')
            lines.append(line)
            lines.append(empty_line)
        return '\n'.join(lines)

@dataclass
class Actor:
    """
    Represents an actor in a plot
    """

    name: str
    column: int
    plot: Plot
    data: dict[str, str] = None

    def __str__(self):
        return f'{self.name}({self.column})'

@dataclass
class Message:
    """
    Represents a message between two actors.

    Attributes:
        sender (str): The sender of the message.
        receiver (str): The receiver of the message.
        bydirectional (bool): Indicates if the message is bidirectional.
        content (str): The content of the message.
        line (int): The line number of the message.
        order (int, optional): The order of the message. Defaults to 0.
        title (str, optional): The title of the message. Defaults to None.
        data (dict[str, str], optional): Additional data associated with the message. Defaults to None.
    """

    sender: Actor
    receiver: Actor
    bydirectional: bool
    content: str
    line: int
    order: int = 0
    title: str = None
    data: dict[str, str] = None

    @property
    def left(self):
        if self.sender.column < self.receiver.column:
            return self.sender
        return self.receiver

    @property
    def right(self):
        if self.sender.column > self.receiver.column:
            return self.sender
        return self.receiver

    def __str__(self):
        direction = '<->' if self.bydirectional else '-->'
        return f"[{self.order}] {self.sender}\t{direction}\t{self.receiver}\t: {self.content!r}"

    def __repr__(self):
        return self.__str__().replace('\t', ' ')

class PlotParser:
    """
    A class that parses data from a file and constructs a plot object.

    Attributes:
        filename (str): The path of the file to be parsed.
        plot (Plot): The plot object to be constructed.
        data (List[str]): The data read from the file.

    Methods:
        __init__(self, filename: str, plot: Plot):
            Initializes the PlotParser object.
        parse(self) -> Plot:
            Parses the data in the file and constructs a plot object.
        parse_line(self, line: str, line_no: int):
            Parses a single line and adds its message to the plot.
        append_data_to_previous_message(self, line: str):
            Appends data to the previous message in the plot.
        get_column_counts(self, line: str) -> tuple[int, int, bool, bool, str, int]:
            Gets the column counts and message direction from a line.
        extract_data(self, line: str, end_of_columns: int, nb_columns_after_message: int) -> str | None:
            Extracts the data from a line.
        get_sender_receiver_direction(self, nb_columns_befor_message: int, nb_columns_after_message: int, message_direction: str) -> tuple[Actor, Actor, bool]:
            Gets the sender, receiver, and direction of a message.
    """

    def __init__(self, filename: str, plot: Plot):
        """
        Initializes the PlotParser object.

        Args:
            filename (str): The path of the file to be parsed.
            plot (Plot): The plot object to be constructed.
        """
        self.filename = filename
        with open(filename, 'r') as file:
            self.data = file.read().split("\n")
        self.plot = plot

    def parse(self) -> Plot:
        """
        Parses the data in the file and constructs a plot object.

        Returns:
            Plot: The constructed plot object.
        """
        # Parse the actors. They are the first line of the file, speparated by multiple spaces.
        actors = self.data[0].split(" ")
        regex_actors = re.compile(r"[A-Za-z0-9_-]+")
        actors = regex_actors.findall(self.data[0])
        self.plot.actors = [Actor(actor, index, self.plot) for index, actor in enumerate(actors)]
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
            self.extract_json_data(message)
        return self.plot

    def extract_json_data(self, message: Message):
        """
        Extracts JSON data from the message content and updates the message object.

        Args:
            message (Message): The message object containing the content to extract JSON data from.

        Raises:
            PlotError: If the JSON data is invalid or incomplete.

        Returns:
            None
        """
        # extract the json data from the message content, if any
        if '{' not in message.content:
            title = message.content.strip().split(' ')[0] if ' ' in message.content else message.content
            message.title = title
            message.content = message.content.strip()[len(title):].strip()
            message.data = {}
            return
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

    def parse_line(self, line: str, line_no: int):
        """
        Parses a single line and adds its message to the plot.

        Args:
            line (str): The line to be parsed.
            line_no (int): The line number.

        Raises:
            PlotError: If there is an error parsing the line.
        """
        regex_line_is_new_message = re.compile(r"\|.*-.*\|.*")
        if not re.match(regex_line_is_new_message, line) and self.plot.messages:
            self.append_data_to_previous_message(line)
            return
        nb_columns_befor_message, nb_columns_after_message, message_found, arrow_ended, message_direction, end_of_columns = self.get_column_counts(line)
        if not message_found:
            return
        data = self.extract_data(line, end_of_columns, nb_columns_after_message)
        if not data:
            raise PlotError("no message content. If you want no operation, use `#` to indicate it wasn't a mistake.", char_number=end_of_columns, line=line)
        sender, receiver, bydirectional = self.get_sender_receiver_direction(nb_columns_befor_message, nb_columns_after_message, message_direction)
        order = len(self.plot.messages)
        message = Message(sender=sender, receiver=receiver, bydirectional=bydirectional, content=data, order=order, line=line_no+2)
        self.plot.messages.append(message)

    def append_data_to_previous_message(self, line: str):
        """
        Appends data to the previous message in the plot.

        Args:
            line (str): The line containing the data to be appended.
        """
        cnt = 0
        i = 0
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

    def get_column_counts(self, line: str) -> tuple[int, int, bool, bool, str, int]:
        """
        Gets the column counts and message direction from a line.

        Args:
            line (str): The line to be analyzed.

        Returns:
            tuple[int, int, bool, bool, str, int]: A tuple containing:
                - The number of columns before the message.
                - The number of columns after the message.
                - A boolean indicating if a message was found.
                - A boolean indicating if the arrow ended.
                - The direction of the message.
                - The index of the end of the columns.
        """
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
        return nb_columns_befor_message, nb_columns_after_message, message_found, arrow_ended, message_direction, end_of_columns


    def extract_data(self, line: str, end_of_columns: int, nb_columns_after_message: int) -> str | None:
        """
        Extracts the data from a line.

        Args:
            line (str): The line to extract data from.
            end_of_columns (int): The index of the end of columns.
            nb_columns_after_message (int): The number of columns after the message.

        Returns:
            str | None: The extracted data, or None if no data is found.
        """
        if nb_columns_after_message > 0:
            data = line[end_of_columns + 1:]
            return data
        return None
    def get_sender_receiver_direction(self, nb_columns_befor_message: int, nb_columns_after_message: int, message_direction: str) -> tuple[Actor, Actor, bool]:
        """
        Gets the sender, receiver, and direction of a message.

        Args:
            nb_columns_befor_message (int): The number of columns before the message.
            nb_columns_after_message (int): The number of columns after the message.
            message_direction (str): The direction of the message.

        Returns:
            tuple[Actor, Actor, bool]: A tuple containing the sender, receiver, and direction of the message.
        """
        index_left_actor = nb_columns_befor_message
        index_right_actor = len(self.plot.actors) - nb_columns_after_message
        left = self.plot.actors[index_left_actor]
        right = self.plot.actors[index_right_actor]
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
        return sender, receiver, bydirectional