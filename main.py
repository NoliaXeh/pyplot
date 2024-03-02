import pyplot

def main():
    plot = pyplot.Plot("Scenario 1", "scenario.plot")
    print(plot.title)
    print(plot.filename)
    try:
        plot.parse()
    except pyplot.PlotError:
        print("Error parsing file. Exiting. ")
    
    pyplot.execute(plot)

@pyplot.action
class PrintAction:
    @staticmethod
    def trigger(plot: pyplot.Plot, message: pyplot.Message) -> bool:
        return True
    
    @staticmethod
    def execute(plot: pyplot.Plot, message: pyplot.Message):
        print(f"""\
Message #{message.order + 1}: {message.content} 
  | From: {message.sender}
  | To: {message.receiver}\
""")


if __name__ == '__main__':
    main()