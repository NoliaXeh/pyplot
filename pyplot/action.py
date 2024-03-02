from .pyplot import Message, Plot

class ActionOverloadError(Exception):
    def __init__(self, obj, function):
        self.obj = obj
        self.function = function
    
    def __str__(self):
        return f"Action {self.obj.__name__}.{self.function} was not implemented."

__plot_actions = {}
def action(classDefinition):
    """
    Decorator to register a class action and check if it was overloaded.
    """
    def check_method(name):
        if not hasattr(classDefinition, name):
            raise ActionOverloadError(classDefinition, name)
    check_method('trigger')
    check_method('execute')

    __plot_actions[classDefinition.__name__] = classDefinition
    return classDefinition

def execute(plot: Plot):
    """
    Execute the actions for the given plot.
    """
    for message in plot.messages:
        for action in __plot_actions.values():
            if action.trigger(plot, message):
                action.execute(plot, message)
                break
    return plot