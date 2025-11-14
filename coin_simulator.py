import socket
import threading


def listen_server(sock):
    while True:
        try:
            data = sock.recv(124)
            if not data:
                break
            msg = data.decode().strip()
            print([f'[listen-server] data: {msg}'])
            if msg == "close_connection":
                print("[coin-simulator] Server requested close. Exiting...")
                break
        except:
            break
    sock.close()
    print("[coin-simulator] client socket closed")
    exit(0)

sock = socket.socket()
sock.connect(("127.0.0.1", 5050))


threading.Thread(target=listen_server, args=(sock,), daemon=True).start()


while True:
    val = input("Insertar tipo, ejemplo billete:20 o moneda:10:  ")
    try:
        sock.send(val.encode())
    except:
        print("[coin-simulator] Could not send, socket closed.")
        break

