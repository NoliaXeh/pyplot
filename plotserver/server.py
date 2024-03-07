from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from .home import *

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/plot-explore', plot_explore),
    Route('/actor-edit/{plot_id:int}/{actor_column:int}', actor_edit),
    Route('/actor-edit/move-left/{actor_column:int}', actor_edit_move_left),
    Route('/actor-edit/move-right/{actor_column:int}', actor_edit_move_right),
    Route('/message-edit/{plot_id:int}/{msg_order:int}', message_edit),
    Route('/message-edit/from_to', message_edit_from_to, methods=['POST']),
    Route('/message-edit/title', message_edit_title, methods=['POST']),
    Route('/message-edit/data', message_edit_data, methods=['POST']),
    Route('/message-edit/delete/{msg_order:int}', message_edit_delete),
    Route('/message-edit/move-up/{msg_order:int}', message_edit_up),
    Route('/message-edit/move-down/{msg_order:int}', message_edit_down),
    Route('/message-new', message_new),
    Mount('/static', app=StaticFiles(directory="plotserver/static"), name="static"),
])