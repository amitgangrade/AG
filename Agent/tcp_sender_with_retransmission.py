import socket
import time

def start_sender(host='127.0.0.1', port=5000, num_packets=10):
    """
    Simulates a sender that waits for application-level ACKs.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Try connecting until successful (wait for receiver to start)
    while True:
        try:
            client_socket.connect((host, port))
            print(f"Connected to receiver at {host}:{port}")
            break
        except ConnectionRefusedError:
            print("Receiver not ready, retrying in 1s...")
            time.sleep(1)

    client_socket.settimeout(1.0) # 1 second timeout for ACKs

    for i in range(1, num_packets + 1):
        packet_msg = f"Packet-{i}"
        ack_received = False
        
        while not ack_received:
            print(f"[SEND] Sending: {packet_msg}")
            client_socket.sendall(packet_msg.encode())
            
            try:
                data = client_socket.recv(1024)
                if data.decode() == "ACK":
                    print(f"[ACK] Received ACK for {packet_msg}")
                    ack_received = True
            except socket.timeout:
                print(f"[TIMEOUT] No ACK for {packet_msg}, retransmitting...")
            except Exception as e:
                print(f"Error: {e}")
                break
        
        time.sleep(0.5) # Small delay between packets

    client_socket.close()
    print("All packets sent and acknowledged.")

if __name__ == "__main__":
    start_sender()
