import socket
import logging
import ssl
import os

server_address = ('localhost', 8885)
# ganti port 8889 untuk process pool

def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def make_secure_socket(destination_address='localhost', port=10000):
    try:
        # get it from https://curl.se/docs/caextract.html

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def send_command(command_str, is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]

    if is_secure:
        sock = make_secure_socket(alamat_server, port_server)
    else:
        sock = make_socket(alamat_server, port_server)

    try:
        logging.warning("sending message ")
        sock.sendall(command_str.encode())
        logging.warning(command_str)

        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        hasil = data_received
        logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False
    finally:
        sock.close()

def send_list():
    cmd = "GET /list HTTP/1.0\r\n\r\n"
    return send_command(cmd, is_secure=False)

def send_upload(filename, content):
    content_bytes = content.encode()
    content_length = len(content_bytes)
    cmd = f"POST /upload HTTP/1.0\r\nFilename: {filename}\r\nContent-Length: {content_length}\r\n\r\n{content}"
    return send_command(cmd, is_secure=False)

def send_delete(filename):
    cmd = f"DELETE /delete?file={filename} HTTP/1.0\r\n\r\n"
    return send_command(cmd, is_secure=False)

# Main logic
if __name__ == '__main__':
    print("=== File di Server ===")
    hasil = send_list()
    print(hasil)

    while True:
        perintah = input("Masukkan perintah (upload <filename> / delete <filename> / exit): ").strip()

        if perintah.lower() == 'exit':
            print("Keluar dari program.")
            break

        elif perintah.startswith('upload '):
            filename = perintah[7:].strip()
            if not os.path.exists(filename):
                print("File tidak ditemukan di direktori lokal!")
                continue
            with open(filename, 'r') as f:
                content = f.read()
            hasil = send_upload(os.path.basename(filename), content)
            print("\n[HASIL UPLOAD]:")
            print(hasil)

        elif perintah.startswith('delete '):
            filename = perintah[7:].strip()
            hasil = send_delete(os.path.basename(filename))
            print("\n[HASIL DELETE]:")
            print(hasil)

        print("\n=== File di Server (Update) ===")
        hasil = send_list()
        print(hasil)
