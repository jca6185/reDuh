#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer 
import socket, select
import cgi
import argparse
import base64
import logging

class ProxyRequestHandler(BaseHTTPRequestHandler):

    sockets = {}
    sockets_ids = {}
    BUFFER = 50*1024
    SOCKET_TIMEOUT = 50

    def _get_connection_id(self):
        return self.path.split('/')[-1]

    def _get_socket(self):
        """get the socket which connects to the target address for this connection"""
        id = self._get_connection_id()
        return self.sockets.get(id, None)

    def _get_id(self, socket):
        return self.sockets_ids.get(socket.fileno(), None)

    def _close_socket(self):
        """ close the current socket"""
        id = self._get_connection_id()
        s = self.sockets[id]
        if s:
            s.close()
            del self.sockets[id]

    def do_GET(self):
        """GET: Read data from TargetAddress and return to client through http response"""
        logging.debug("READ DATA REQUEST")
        sockets = self.sockets
        if sockets:
            # check if the socket is ready to be read
            logging.debug("Waiting...")
            to_reads, to_writes, in_errors = select.select(sockets.values(), [], [], 5)
            if len(to_reads) > 0: 
                to_read_socket = to_reads[0]
                try:
                    data = to_read_socket.recv(self.BUFFER)
                    if data:
                        self.send_response(200)
                        self.end_headers()

                        (remoteAddr, remotePort) = to_read_socket.getpeername()
                        response = '[data]' + remoteAddr + ':' + str(remotePort) + ':' + str(self._get_id(to_read_socket)) + ':' + base64.b64encode(data)

                        logging.debug("Received: " + response)
                        self.wfile.write(response)
                    else:
                        self.no_new_data()
                except Exception, ex:
                    logging.debug("Error: " + `ex`)
                    self.send_response(503)
                    self.end_headers()
            else:
                self.no_new_data()
        else:
            self.no_new_data()

    def no_new_data(self):
        logging.debug("No data to read")
        self.send_response(200) # no content had be retrieved
        self.end_headers()
        self.wfile.write('[NO_NEW_DATA]')

    def do_POST(self):
        """POST: Create TCP Connection to the TargetAddress"""
        id = self._get_connection_id() 
        logging.debug("OPEN SOCKET REQUEST ON:" + str(id))
        length = int(self.headers.getheader('content-length'))
        req_data = self.rfile.read(length)
        params = cgi.parse_qs(req_data, keep_blank_values=1)
        
        if 'die' in params:
        	sys.exit(0)

        target_host = params['host'][0]
        target_port = int(params['port'][0])

        # open socket connection to remote server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # use non-blocking socket
        s.setblocking(0)
        s.connect_ex((target_host, target_port))

        #save socket reference
        logging.debug("Socket created")
        self.sockets_ids[s.fileno()] = id
        self.sockets[id] = s
        try: 
            self.send_response(200)
            self.end_headers()
        except socket.error, e:
            self.send_response(503)
            self.end_headers()

    def do_PUT(self):
        """Read data from HTTP Request and send to TargetAddress"""
        id = self._get_connection_id()
        logging.debug("WRITE TO SOCKET REQUEST ON:" + str(id))
        s = self.sockets[id]
        if not s:
            logging.debug("Socket not found")
            self.send_response(400)
            self.end_headers()
            return

        length = int(self.headers.getheader('content-length'))
        params = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        data = params['data'][0].replace(" ", "+")

        if data == '*':
            logging.debug("Request to close socket")
            self.do_DELETE()
            return

        data = base64.b64decode(data)

        # check if the socket is ready to write
        to_reads, to_writes, in_errors = select.select([], [s], [], 5)
        if len(to_writes) > 0: 
            logging.debug("Ready to write")
            to_write_socket = to_writes[0]
            try: 
                to_write_socket.sendall(data)
                self.send_response(200)
                self.end_headers()
                logging.debug("Written: " + data)
            except socket.error as ex:
                self.send_response(503)
                self.end_headers()
                logging.debug("Could not write")
        else:
            logging.debug("Socket was not ready to write, close")
            self.send_response(200)
            self.end_headers()
            self.wfile.write('[data]'+str(id)+':*')

    def do_DELETE(self): 
        self._close_socket()
        self.send_response(200)
        self.end_headers()

def run_server(port, server_class=HTTPServer, handler_class=ProxyRequestHandler): 
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.debug("Starting...")
    httpd.serve_forever()

def start_log():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s',
                        filename='reDuh.log', filemode='w')

if __name__ == "__main__":
    start_log()
    parser = argparse.ArgumentParser(description="Start Tunnel Server")
    parser.add_argument("-p", default=9999, dest='port', help='Specify port number server will listen to', type=int)
    args = parser.parse_args()
    run_server(args.port)