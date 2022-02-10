# The sanic server.

import os
import signal
import json
from sanic import Sanic
from muddery.common.utils.utils import write_pid_file, read_pid_file
from muddery.common.networks import responses
from muddery.launcher.manager import collect_worldeditor_static
from muddery.worldeditor.server import Server
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.utils.logger import logger


def run():
    # Check if a server is running.
    pid = read_pid_file(SETTINGS.WORLD_EDITOR_PID)
    if pid:
        print('\nThe worldeditor server has already started.\nYou can run "muddery stop" to stop it and start it again.')
        return

    # run the network
    app = Sanic("muddery_worldeditor")

    @app.before_server_start
    async def before_server_start(app, loop):
        # init the worldeditor server
        Server.inst().init()

        # collect static files
        collect_worldeditor_static()

    @app.after_server_start
    async def after_server_start(app, loop):
        # save pid
        write_pid_file(SETTINGS.WORLD_EDITOR_PID, os.getpid())
        print("\nWorldeditor server started.\n")

    @app.after_server_stop
    async def after_server_stop(app, loop):
        # server stopped
        try:
            os.remove(SETTINGS.WORLD_EDITOR_PID)
        except:
            pass
        print("Worldeditor server stopped.")

    # static web pages
    app.static('/editor', SETTINGS.WORLD_EDITOR_WEBROOT)
    app.static('/media', SETTINGS.MEDIA_ROOT)

    # check the server's status
    @app.get("/status")
    async def get_status(request):
        return responses.success_response()

    # api
    @app.post(SETTINGS.WORLD_EDITOR_API_PATH + "/<func>")
    async def handler(request, func):
        token = request.headers.get("Authorization")
        if token:
            token_prefix = "Bearer "
            if token.find(token_prefix) == 0:
                token = token[len(token_prefix):]

        if request.content_type == "application/json":
            data = request.json
        elif request.content_type == "application/x-www-form-urlencoded":
            data = {}
            if "func_no" in request.form and len(request.form["func_no"]) > 0:
                data["func_no"] = json.loads(request.form["func_no"][0])
            if "args" in request.form and len(request.form["args"]) > 0:
                data["args"] = json.loads(request.form["args"][0])
            if "token" in request.form and len(request.form["token"]) > 0:
                token = request.form["token"][0]
        elif request.content_type.index("multipart/form-data;") == 0:
            data = request.form
        else:
            data = None

        response = await Server.inst().handle_request(request.method, request.path, data, token)

        if hasattr(response, "body"):
            print("[RESPOND] '%s' '%s'" % (response.status, response.body))
            logger.log_info("[RESPOND] '%s' '%s'" % (response.status, response.body))
        elif hasattr(response, "streaming_content"):
            logger.log_info("[RESPOND] '%s' streaming_content" % response.status)
        else:
            logger.log_info("[RESPOND] '%s'" % response.status)

        return response

    # run the server
    app.run(port=SETTINGS.WORLD_EDITOR_PORT)


def stop():
    # Send a terminate signal to the server.
    pid = read_pid_file(SETTINGS.WORLD_EDITOR_PID)
    if not pid:
        print("Can not get the worldeditor server's pid.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        print("Worldeditor server stopped.")
    except:
        print("Can not stop the worldeditor server correctly.")

    try:
        os.remove(SETTINGS.WORLD_EDITOR_PID)
    except:
        pass
