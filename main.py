import pyplot

def main():
    plot = pyplot.Plot("Scenario 1", "scenarios/scenario.plot")
    try:
        plot.parse()
    except pyplot.PlotError as e:
        print("Error parsing file. Exiting. ")
        print (e)
        return 1

    print(pyplot.play(plot))

#@pyplot.action
class PrintAction:
    @staticmethod
    def trigger(plot: pyplot.Plot, message: pyplot.Message) -> bool:
        return True

    @staticmethod
    def execute(plot: pyplot.Plot, message: pyplot.Message):
        print(f"""\
Message #{message.order + 1}: {message.title!r}
  | From: {message.sender}
  | To: {message.receiver}
  | Content: {message.content}
  | Data: {message.data}\
""")

def print_message(plot, message: pyplot.Message):
    print(message)

def trigger_if_message(plot, message: pyplot.Message):
    return message.title.upper() == 'MESSAGE'

@pyplot.action
@pyplot.trigger_on_title('MESSAGE')
@pyplot.execute(print_message)
class PrintMessageAction:
    pass


@pyplot.template_action
class TemplateAction:
    message = "MESSAGE"
    template = 'templates/template.templ'


if __name__ == '__main__':
    exit(main())