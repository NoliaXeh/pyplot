import jinja2
from .pyplot import Message, Plot

class ActionOverloadError(Exception):
    """
    Exception raised when an action overload is encountered.

    Attributes:
        obj (type): The object that the action belongs to.
        function (str): The name of the function that was not implemented.
    """

    def __init__(self, obj, function):
        self.obj = obj
        self.function = function

    def __str__(self):
        return f"Action {self.obj.__name__}.{self.function} was not implemented."

__plot_actions = {}
def action(classDefinition):
    """
    Decorator to register a class action and check if it was overloaded.

    Args:
        classDefinition: The class to be registered as an action.

    Raise:
        ActionOverloadError: If the class does not have the required methods 'trigger' and 'execute'.

    Returns:
        The registered class.
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
    """
    Applies a template-based action to a plot.
    It looks for a "template" attribute in the class definition and uses it to render the message.
    It also looks for a "message" attribute in the class definition and uses it to match the message title.

    Args:
        classDefinition: The class definition containing the action details.

    Returns:
        The action object.

    Raises:
        None.
    """

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
    Executes the actions defined in the plot for each message.

    Args:
        plot (Plot): The plot containing the messages and actions.

    Returns:
        str: The result of executing the actions.
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