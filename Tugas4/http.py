import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}: {}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''.join(resp)

        if not isinstance(messagebody, bytes):
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        try:
            headers_part, body = data.split('\r\n\r\n', 1)
        except ValueError:
            headers_part = data
            body = ''

        lines = headers_part.split('\r\n')
        request_line = lines[0]
        headers_lines = lines[1:]

        headers = {}
        for h in headers_lines:
            if ': ' in h:
                key, val = h.split(': ', 1)
                headers[key.lower()] = val.strip()

        parts = request_line.split(' ')
        if len(parts) < 3:
            return self.response(400, 'Bad Request', 'Invalid Request Line')

        method = parts[0].upper()
        path = parts[1]

        if method == 'GET':
            return self.http_get(path, headers)
        elif method == 'POST':
            return self.http_post(path, headers, body)
        elif method == 'DELETE':
            return self.http_delete(path, headers)
        else:
            return self.response(405, 'Method Not Allowed', 'Method not supported')

    def http_get(self, path, headers):
        if path == '/list':
            files = [os.path.basename(f) for f in glob('./*') if os.path.isfile(f)]
            daftar = "\n".join(files)
            return self.response(200, 'OK', daftar, {'Content-Type': 'text/plain'})

        if path == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {})

        filepath = path.lstrip('/')
        if not os.path.isfile(filepath):
            return self.response(404, 'Not Found', 'File not found')

        ext = os.path.splitext(filepath)[1]
        content_type = self.types.get(ext, 'application/octet-stream')

        with open(filepath, 'rb') as f:
            isi = f.read()

        return self.response(200, 'OK', isi, {'Content-Type': content_type})

    def http_post(self, path, headers, body):
        if path == '/upload':
            filename = headers.get('filename')
            content_length = headers.get('content-length')

            if not filename:
                return self.response(400, 'Bad Request', 'Filename header missing')

            if content_length:
                try:
                    content_length = int(content_length)
                except ValueError:
                    return self.response(400, 'Bad Request', 'Invalid Content-Length')

                content = body[:content_length]
            else:
                content = body

            try:
                with open(filename, 'wb') as f:
                    f.write(content.encode() if isinstance(content, str) else content)
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Gagal menyimpan file: {e}')

            return self.response(200, 'OK', f'File {filename} berhasil diupload')

        return self.response(404, 'Not Found', 'Path tidak ditemukan')

    def http_delete(self, path, headers):
        parsed_url = urlparse(path)
        if parsed_url.path != '/delete':
            return self.response(404, 'Not Found', 'Path tidak ditemukan')

        query = parse_qs(parsed_url.query)
        files = query.get('file', [])
        if not files:
            return self.response(400, 'Bad Request', 'Parameter file tidak ada')

        filename = files[0]
        if not os.path.isfile(filename):
            return self.response(404, 'Not Found', 'File tidak ditemukan')

        try:
            os.remove(filename)
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Gagal menghapus file: {e}')

        return self.response(200, 'OK', f'File {filename} berhasil dihapus')

if __name__ == "__main__":
    httpserver = HttpServer()

    request = "GET /list HTTP/1.0\r\n\r\n"
    resp = httpserver.proses(request)
    print(resp.decode())

    content = "Ini adalah isi file"
    content_length = len(content)
    request = (
        f"POST /upload HTTP/1.0\r\n"
        f"Filename: test_upload.txt\r\n"
        f"Content-Length: {content_length}\r\n\r\n"
        f"{content}"
    )
    resp = httpserver.proses(request)
    print(resp.decode())

    request = "DELETE /delete?file=test_upload.txt HTTP/1.0\r\n\r\n"
    resp = httpserver.proses(request)
    print(resp.decode())
