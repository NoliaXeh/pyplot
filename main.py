import pyplot

def main():
    plot = pyplot.Plot("Scenario 1", "scenario.plot")
    print(plot.title)
    print(plot.filename)
    try:
        plot.parse()
    except pyplot.PlotError:
        print("Error parsing file. Exiting. ")


if __name__ == '__main__':
    main()