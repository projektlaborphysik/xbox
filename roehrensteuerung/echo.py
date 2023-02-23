#!/usr/bin/env python3
# Example of simple echo server
# www.solusipse.net
import sys
import socket

def listen():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(('127.0.0.1', 50001))
    connection.listen(10)
    while True:
        current_connection, address = connection.accept()
        while True:
            data = current_connection.recv(2048)
            if data == 'quit\r\n':
                current_connection.shutdown(1)
                current_connection.close()
                break

            elif data == 'stop\r\n':
                current_connection.shutdown(1)
                current_connection.close()
                exit()

            elif data:
                print(data)
                #current_connection.send(data)
                #dummy_data = ''.join(['\x02', '32,', '1,', '0,', '0,', '0,', '0,', '0,', '0,', '\x03']).encode()
                dummy_data = ''.join(['\x02', '20,', '2048,', '4095,', '3500,', '3000,', '4000,', '512,', '2048,', '\x03', '\x02', '32,', '1,', '0,', '0,', '0,', '0,', '0,', '0,', '\x03']).encode()
                current_connection.send(dummy_data)
                


if __name__ == "__main__":
    try:
        listen()
    except KeyboardInterrupt:
        pass
