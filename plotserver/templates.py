from jinja2 import Environment, FileSystemLoader
import json as JSON

def json(dic):
    return JSON.dumps(dic, indent=4)


env = Environment(loader=FileSystemLoader('plotserver/templates'))

env.filters['json'] = json

templates = {}

DEBUG = True

def get_template(name):
    if DEBUG or name not in templates:
        templates[name] = env.get_template(name)
    return templates[name]