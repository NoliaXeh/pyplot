import pyplot

def main():
    plot = pyplot.Plot("Scenario 1", "scenario.plot")
    print(plot.title)
    print(plot.filename)
    try:
        plot.parse()
    except pyplot.PlotError as e:
        print("Error parsing file. Exiting. ")
        print (e)
        return 1

    pyplot.execute(plot)

@pyplot.action
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


if __name__ == '__main__':
    exit(main())