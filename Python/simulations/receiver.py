import socket
import random
import time

def start_receiver(host='127.0.0.1', port=12345, loss_rate=0.01):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Receiver listening on {host}:{port} with {loss_rate*100}% packet loss...")

    expected_seq_num = 0
    total_received = 0
    total_pkts = 0
    dropped_pkts = 0

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            total_pkts += 1
            
            # Simulate packet loss
            if random.random() < loss_rate:
                print(f"DEBUG: Dropping packet with seq {data.decode().split('|')[0]}")
                dropped_pkts += 1
                continue

            try:
                msg = data.decode()
                seq_num_str, payload = msg.split('|', 1)
                seq_num = int(seq_num_str)
                
                if seq_num == expected_seq_num:
                    # print(f"Received in-order: {seq_num}")
                    expected_seq_num += 1
                    total_received += len(payload)
                else:
                    # Ignore out-of-order packets (Go-Back-N)
                    # print(f"Received out-of-order: {seq_num}, expected: {expected_seq_num}")
                    pass
                
                # Cumulative ACK: acknowledge the highest in-order sequence number received
                ack = str(expected_seq_num - 1).encode()
                sock.sendto(ack, addr)
                
                if payload == "EOF":
                    print("\n--- Transmission Complete ---")
                    print(f"Total packets handled: {total_pkts}")
                    print(f"Packets dropped (simulated): {dropped_pkts}")
                    print(f"Actual loss rate: {(dropped_pkts/total_pkts)*100:.2f}%")
                    print(f"Total data received: {total_received - 3} bytes") # subtract 'EOF' size
                    # Reset for next run or exit
                    expected_seq_num = 0
                    total_received = 0
                    total_pkts = 0
                    dropped_pkts = 0

            except Exception as e:
                print(f"Error processing packet: {e}")

    except KeyboardInterrupt:
        print("\nReceiver shutting down.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_receiver()
