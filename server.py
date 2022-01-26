#  coding: utf-8
import socketserver
import os
import mimetypes
from email.utils import formatdate

# Copyright 2022 Abram Hindle, Eddie Antonio Santos, Nathan Tang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        '''
        Handle HTTP requests and return HTTP responses
        '''

        ENCODING = 'utf-8'
        STATUS_200 = {'code': 200, 'message': "HTTP/1.1 200 OK"}
        STATUS_301 = {'code': 301, 'message': "HTTP/1.1 301 Moved Permanently"}
        STATUS_404 = {'code': 404, 'message': "HTTP/1.1 404 Not Found"}
        STATUS_405 = {'code': 405, 'message': "HTTP/1.1 405 Method Not Allowed"}

        self.data = self.request.recv(1024).strip()
        request, *options = self.data.decode(ENCODING).split("\r\n")
        print(request)
        method, path, version = request.split(' ')

        # Only supports GET method
        if method != 'GET':
            response = self.send_response(STATUS_405)

        # Check if path is being falsified
        elif not os.path.realpath(f"./www/{path}").startswith(os.path.realpath("./www")):
            response = self.send_response(STATUS_404)

        # Check if dir
        elif os.path.isdir(f"./www/{path}") and not path.endswith('/'):
            response = self.send_response(STATUS_301, location=f"{path}/")

        # If requesting a dir
        elif os.path.isdir(f"./www/{path}") and path.endswith('/'):
            file = open(f"./www/{path}/index.html", "r")
            lines = file.read()
            file.close()
            content = {
                'content': lines,
                'length': len(lines.encode(ENCODING)),
                'type': f"text/html; charset={ENCODING}"
            }
            response = self.send_response(STATUS_200, content=content)

        # If requesting a specific file
        elif os.path.exists(f"./www/{path}"):
            file = open(f"./www/{path}", "r")
            lines = file.read()
            file.close()
            content = {
                'content': lines,
                'length': len(lines.encode(ENCODING)),
                'type': mimetypes.guess_type(f"./www/{path}")[0]
            }
            response = self.send_response(STATUS_200, content=content)

        # Return 404 if nothing is found
        else:
            response = self.send_response(STATUS_404)

        return self.request.sendall(bytearray(response, ENCODING))

    def send_response(self, status, content = None, location = None):
        '''
        Build the response for the request using HTTP headers and body

        Parameters
        ---
        status : dict
            HTTP status with a code and message
        content : dict
            Content information with type, length, and body
        location : str
            Location path for 301 redirects

        Returns
        ---
        response : str
            A response string
        '''
        response = f"{status['message']}\r\n"
        response += f"Server: nathanlytang/0.1\r\n"
        response += f"Date: {formatdate(timeval=None, localtime=False, usegmt=True)}\r\n"
        if status['code'] == 405:
            response += f"Allow: GET\r\n"
        # Redirect to proper location if 301
        if location is not None:
            response += f"Location: {location}\r\n"
        # Add content information
        if content is not None:
            response += f"Content-Type: {content['type']}\r\n"
            response += f"Content-Length: {content['length']}\r\n"
            response += f"\r\n{content['content']}"
        return response

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
