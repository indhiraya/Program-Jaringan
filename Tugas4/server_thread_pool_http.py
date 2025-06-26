from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan threadpool executor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def recv_all(connection):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = connection.recv(1024)
        if not chunk:
            break
        data += chunk

    if b"\r\n\r\n" not in data:
        return data.decode(errors='ignore')

    header_data, rest = data.split(b"\r\n\r\n", 1)
    headers_text = header_data.decode(errors='ignore').split("\r\n")
    request_line = headers_text[0]
    headers = {}

    for h in headers_text[1:]:
        if ': ' in h:
            k, v = h.split(': ', 1)
            headers[k.lower()] = v

    content_length = int(headers.get('content-length', '0'))
    while len(rest) < content_length:
        chunk = connection.recv(1024)
        if not chunk:
            break
        rest += chunk

    full_request = header_data + b"\r\n\r\n" + rest
    return full_request.decode(errors='ignore')

def ProcessTheClient(connection, address):
    try:
        request_data = recv_all(connection)
        response = httpserver.proses(request_data)
        if not isinstance(response, bytes):
            response = response.encode()

        connection.sendall(response)
    except Exception as e:
        logging.error(f"Error processing request from {address}: {e}")
    finally:
        connection.close()

def Server():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(20)
    print("Server started on port 8885")

    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            executor.submit(ProcessTheClient, connection, client_address)

def main():
    Server()

if __name__ == "__main__":
    main()
