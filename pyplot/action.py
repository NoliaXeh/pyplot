import jinja2
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

__templates = {}
def template_action(classDefinition):
    if not hasattr(classDefinition, 'trigger'):
        if hasattr(classDefinition, 'message'):
            message_title = classDefinition.message
            def __match_title(plot, message):
                return message_title == message.title
            setattr(classDefinition, 'trigger', __match_title)

    if not hasattr(classDefinition, 'execute'):
        if hasattr(classDefinition, 'template'):
            template_name = classDefinition.template
            if template_name not in __templates:
                __templates[template_name] = None
            def __run_template(plot, message):
                template = __templates[template_name]
                return template.render(message=message) + '\n'
            setattr(classDefinition, 'execute', __run_template)
    return action(classDefinition)


def play(plot: Plot):
    """
    Execute the actions for the given plot.
    """
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    for template_name in __templates:
        __templates[template_name] = environment.get_template(template_name)

    result = ''
    for message in plot.messages:
        for action in __plot_actions.values():
            if action.trigger(plot, message):
                res = action.execute(plot, message)
                if type(res) is str:
                    result += res
    return result