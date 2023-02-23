#!/usr/bin/env python3
# Example of simple echo server
# www.solusipse.net
import sys
import socket

Start = b'\x02'
End = b',\x03'

def get_response(current_connection):
        total_data=[]
        data=''
        while True:
            try:
                data=current_connection.recv(2048)
                
            except socket.error as exc:
                print('Failed to get response: %s' % exc)
                pass
            
            if Start in data:
                total_data.append(data[data.find(Start)+len(Start):])
                
            elif End in data:
                total_data.append(data[:data.find(End)])
                break
            
            else:
                total_data.append(data)
            
            #check if end_of_data was split
            if len(total_data)>1:
                last_pair=total_data[-2]+total_data[-1]
                
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
        
        response_string = (b''.join(total_data)).decode()
        
        command_id, *arguments = response_string.split(',')
        return command_id, arguments

def listen():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(('127.0.0.1', 50001))
    connection.listen(10)
    
    while True:
        response = ''
        current_connection, address = connection.accept()
        command_id, arguments = get_response(current_connection)
        print(command_id)
        print(arguments)
        
        
        if command_id == '20':
            response = "\x0220,500,2048,4095,4095,4095,4095,4095,4095,650,\x03"
        
        elif command_id == '32':
            response = "\x0232,1,0,0,0,0,1,0,\x03"
        
        else:
            response = ("\x02%s,$,\x03" % command_id)
            
        print(response.encode())
        current_connection.sendall(response.encode())
        
    '''    
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
                response = "\x0210,$,\x03"
                current_connection.sendall(response.encode())
                print(data)
                #current_connection.close()
                #break
    '''
    
    
if __name__ == "__main__":
    try:
        listen()
    except KeyboardInterrupt:
        sys.exit()
