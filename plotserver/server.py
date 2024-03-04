from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from .home import homepage, message_edit, message_edit_from_to

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/message-edit/{plot_id:int}/{msg_order:int}', message_edit),
    Route('/message-edit/from_to', message_edit_from_to, methods=['POST']),
    Mount('/static', app=StaticFiles(directory="plotserver/static"), name="static"),
])