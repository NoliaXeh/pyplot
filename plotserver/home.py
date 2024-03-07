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
    return current_plot


async def homepage(request):
    # get the 'file' query parameter
    query_params = parse_qs(request.url.query)
    file = query_params.get('file', [None])[0]
    if file is not None:
        global current_plot
        current_plot = pyplot.Plot("Scenario 1", file)
        try:
            current_plot.parse()
        except pyplot.PlotError as e:
            return HTMLResponse(f"Error parsing file. Exiting. <br> <pre>{e}</pre>")

    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('base.html')

    resp = template.render(plot=plot)

    return HTMLResponse(resp)

async def actor_edit(request):
    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('frag/actor-edit.html')

    actor_column = request.path_params.get('actor_column')
    if actor_column is None:
        return HTMLResponse("not found", status_code=404)
    plot.save()

    resp = template.render(actor=plot.actors[actor_column])

    return HTMLResponse(resp)

async def actor_edit_move_left(request):
    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('frag/plot.html')

    actor_column = request.path_params.get('actor_column')
    if actor_column is None:
        return HTMLResponse("not found", status_code=404)

    if actor_column > 0 and len(plot.actors) > 1:
        actor = plot.actors.pop(actor_column)
        actor.column -= 1
        plot.actors[actor_column-1].column += 1
        plot.actors.insert(actor_column - 1, actor)
        plot.save()

    resp = template.render(plot=plot)

    return HTMLResponse(resp)

async def actor_edit_move_right(request):
    plot = get_plot()
    if type(plot) is HTMLResponse:
        return plot

    template = get_template('frag/plot.html')

    actor_column = request.path_params.get('actor_column')
    if actor_column is None:
        return HTMLResponse("not found", status_code=404)

    if actor_column < len(plot.actors) - 1 and len(plot.actors) > 1:
        actor = plot.actors.pop(actor_column)
        actor.column += 1
        plot.actors[actor_column].column -= 1
        plot.actors.insert(actor_column +1 , actor)
        plot.save()

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
    plot.save()

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
        plot.save()

    resp = template.render(plot=plot)

    return HTMLResponse(resp)

async def plot_explore(request):
    # recursivly search for .plot or .pyplot files
    def find_files(path):
        res = {}
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".plot") or file.endswith(".pyplot"):
                    yield os.path.join(root, file)
                    if root not in res:
                        res[root] = []
                    res[root].append(file)
    files = list(find_files("."))

    template = get_template('frag/plot-explorer.html')

    resp = template.render(files=files, selected_file=current_plot.filename if current_plot is not None else None)
    return HTMLResponse(resp)
