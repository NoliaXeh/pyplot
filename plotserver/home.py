from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from urllib.parse import parse_qs

from .templates import get_template

import os

import pyplot

def to_int(s: str) -> int | None:
    try:
        return int(s)
    except:
        return None

global current_plot
current_plot = None

def get_plot():
    global current_plot
    if current_plot is None:
        current_plot = pyplot.Plot("Scenario 1", "scenarios/scenario.plot")
        try:
            current_plot.parse()
        except pyplot.PlotError as e:
            return HTMLResponse(f"Error parsing file. Exiting. <br> <pre>{e}</pre>")
    return current_plot


async def homepage(request):
    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('base.html')

    resp = template.render(plot=plot)

    return HTMLResponse(resp)

async def message_edit(request):
    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('frag/message-edit.html')

    order = request.path_params.get('msg_order')
    if order is None:
        return HTMLResponse("not found", status_code=404)

    resp = template.render(message=plot.messages[order])

    return HTMLResponse(resp)

async def message_edit_from_to(request):
    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('frag/plot.html')

    
    body = await request.json()
    order = to_int(body.get('order'))
    msg_from = to_int(body.get('from'))
    msg_to = to_int(body.get('to'))

    if None in (order, msg_from, msg_to):
        return HTMLResponse("not found", status_code=404)
    
    if msg_to != msg_from:
        plot.messages[order].sender = plot.actors[msg_from]
        plot.messages[order].receiver = plot.actors[msg_to]

    resp = template.render(plot=plot)

    return HTMLResponse(resp)

async def plot_explore(request):
    # recursivly search for .plot or .pyplot files
    def find_files(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".plot") or file.endswith(".pyplot"):
                    yield os.path.join(root, file)
    files = list(find_files("scenarios"))

    