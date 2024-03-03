from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from .templates import get_template

import pyplot

async def homepage(request):
    plot = pyplot.Plot("Scenario 1", "scenarios/scenario.plot")
    try:
        plot.parse()
    except pyplot.PlotError as e:
        return HTMLResponse(f"Error parsing file. Exiting. <br> <pre>{e}</pre>")

    template = get_template('base.html')

    resp = template.render(plot=plot)

    return HTMLResponse(resp)

async def message_edit(request):
    plot = pyplot.Plot("Scenario 1", "scenarios/scenario.plot")
    try:
        plot.parse()
    except pyplot.PlotError as e:
        return HTMLResponse(f"Error parsing file. Exiting. <br> <pre>{e}</pre>")

    template = get_template('frag/message-edit.html')

    order = request.path_params.get('msg_order')
    if order is None:
        return HTMLResponse("not found", status_code=404)

    resp = template.render(message=plot.messages[order])

    return HTMLResponse(resp)
