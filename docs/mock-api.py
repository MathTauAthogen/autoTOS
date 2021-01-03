# mock-api.py
#
# A simple mock Python HTTP server to test the display using dummy data.

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json
from test import test

# port number for test server
PORT = 3000


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/":
                self.path = "/index.html"

            if self.path[-5:] == ".html":
                with open("." + self.path, "r") as document:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(document.read().encode("utf-8"))

            elif self.path[-3:] == ".js":
                with open("." + self.path, "r") as script:
                    self.send_response(200)
                    self.send_header("Content-type", "text/javascript")
                    self.end_headers()
                    self.wfile.write(script.read().encode("utf-8"))

            elif self.path[-4:] == ".css":
                with open("." + self.path, "r") as stylesheet:
                    self.send_response(200)
                    self.send_header("Content-type", "text/css")
                    self.end_headers()
                    self.wfile.write(stylesheet.read().encode("utf-8"))

            elif self.path[-4:] == ".svg":
                print(self.path)
                with open("." + self.path, "rb") as img:
                    print("here")
                    self.send_response(200)
                    self.send_header("Content-type", "image/svg+xml")
                    self.end_headers()
                    text = img.read()
                    self.wfile.write(text)

            else:
                with open("." + self.path, "rb") as file:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(file.read())

        except:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 not found")

    def do_POST(self):
        try:
            if self.path == "/api/parse":
                length = int(self.headers.get("content-length"))
                request = json.loads(self.rfile.read(length))

                if request["text"] == "error":
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"400 bad request")

                elif request["text"] == "blank":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {"predictions": [{"predictions": [], "sentiment": 0}]}
                        ).encode("utf-8")
                    )

                elif request["text"] == "mock":
                    with open("mock-response.json", "r") as dummy:
                        response = json.loads(dummy.read())
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode("utf-8"))

                else:
                    with open("wayfair-response.json", "r") as dummy:
                        response = json.loads(dummy.read())
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.send_header("Vary", "Accept-Encoding, Origin")
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode("utf-8"))

            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 not found")

        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"500 internal server error")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-PINGOTHER, Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Vary", "Accept-Encoding, Origin")
        self.end_headers()


print("Serving on port %d" % PORT)
HTTPServer(("0.0.0.0", PORT), RequestHandler).serve_forever()
