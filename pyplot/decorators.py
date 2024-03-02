from .action import ActionOverloadError
from .pyplot import Actor, Message, Plot
import jinja2

def trigger(function):
    def decorator(classDefinition):
        if not hasattr(classDefinition, 'trigger'):
            setattr(classDefinition, 'trigger', function)
        return classDefinition
    return decorator

def execute(function):
    def decorator(classDefinition):
        if not hasattr(classDefinition, 'execute'):
            setattr(classDefinition, 'execute', function)
        return classDefinition
    return decorator

def trigger_on_title(message_title: str):
    def decorator(classDefinition):
        if not hasattr(classDefinition, 'trigger'):
            setattr(classDefinition, 'trigger', lambda plot, message: message.title.upper() == message_title)
        return classDefinition
    return decorator

