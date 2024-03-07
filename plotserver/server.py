from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from .home import homepage, message_edit, message_edit_from_to, plot_explore, actor_edit, actor_edit_move_left, actor_edit_move_right

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/plot-explore', plot_explore),
    Route('/actor-edit/{plot_id:int}/{actor_column:int}', actor_edit),
    Route('/actor-edit/move-left/{actor_column:int}', actor_edit_move_left),
    Route('/actor-edit/move-right/{actor_column:int}', actor_edit_move_right),
    Route('/message-edit/{plot_id:int}/{msg_order:int}', message_edit),
    Route('/message-edit/from_to', message_edit_from_to, methods=['POST']),
    Mount('/static', app=StaticFiles(directory="plotserver/static"), name="static"),
])