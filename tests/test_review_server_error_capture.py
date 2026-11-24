import ast
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import sys
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize("error,expected", [(ValueError("handler failure"), ["ValueError"]),
                                          (BrokenPipeError(), []), (ConnectionResetError(), [])])
def test_regression_records_handler_error_with_python310_exception_api(error, expected):
    source = Path(__file__).parents[1] / ".github/scripts/investment_review_regression.py"
    node = next(n for n in ast.parse(source.read_text(encoding="utf-8")).body
                if isinstance(n, ast.ClassDef) and n.name == "CheckedServer")
    class Base:
        def handle_error(self, *args):
            pass
    # Python 3.10 has exc_info but no sys.exception. No browser/server or network.
    namespace = {"ThreadingHTTPServer": Base, "sys": SimpleNamespace(exc_info=sys.exc_info)}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), namespace)
    server = namespace["CheckedServer"]()
    try:
        raise error
    except type(error):
        server.handle_error(None, None)
    assert server.unhandled_errors == expected


@pytest.mark.skipif(not hasattr(socket, "SO_EXCLUSIVEADDRUSE"), reason="Windows Winsock listener behavior")
def test_review_exclusively_owns_its_loopback_listener():
    from tradingagents.charting.server import _ReviewServer

    with _ReviewServer(("127.0.0.1", 0), BaseHTTPRequestHandler) as current:
        assert current.socket.getsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE) == 1
        with pytest.raises(OSError):
            ThreadingHTTPServer(current.server_address, BaseHTTPRequestHandler)
