import socket
import random
import time

def start_receiver(host='127.0.0.1', port=5000, drop_rate=0.5):
    """
    Simulates a receiver that randomly drops packets.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"Receiver listening on {host}:{port} with {drop_rate*100}% drop rate...")
    
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")
    
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            packet_msg = data.decode()
            
            # Randomly decide to drop the packet
            if random.random() < drop_rate:
                print(f"[DROP] Received: {packet_msg} -> Purposely ignoring (no ACK)")
                continue
            
            print(f"[OK] Received: {packet_msg} -> Sending ACK")
            conn.sendall(b"ACK")

if __name__ == "__main__":
    start_receiver()
