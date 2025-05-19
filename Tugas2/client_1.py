import socket

def main():
    server_address = ('172.16.16.101', 45000)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    try:
        while True:
            user_input = input()

            request = user_input + "\r\n"

            sock.sendall(request.encode('utf-8'))

            data = sock.recv(1024)
            response = data.decode('utf-8')

            print(response.strip())

            if response.strip() == "Keluar":
                break

    finally:
        sock.close()

if __name__ == "__main__":
    main()
