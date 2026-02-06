import socket
import random
import time

def start_receiver(host='127.0.0.1', port=12345):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Network Receiver listening on {host}:{port}")

    current_loss_rate = 0.0
    current_rtt_s = 0.0  # Round Trip Time in seconds
    expected_seq_num = 0
    total_received = 0
    total_pkts = 0
    dropped_pkts = 0

    try:
        while True:
            data, addr = sock.recvfrom(2048)
            msg = data.decode()
            
            # Simulate one-way trip delay (RTT / 2)
            if current_rtt_s > 0:
                time.sleep(current_rtt_s / 2.0)

            # Handle commands
            if msg.startswith("CMD:SET_LOSS:"):
                current_loss_rate = float(msg.split(":")[2])
                print(f"\n--- New Run: Loss={current_loss_rate*100}%, RTT={current_rtt_s*1000:.1f}ms ---")
                expected_seq_num = 0
                total_received = 0
                total_pkts = 0
                dropped_pkts = 0
                sock.sendto(b"ACK_CMD", addr)
                continue
            
            if msg.startswith("CMD:SET_RTT:"):
                current_rtt_s = float(msg.split(":")[2]) / 1000.0  # Convert ms to s
                print(f"RTT updated to {current_rtt_s*1000:.1f}ms")
                sock.sendto(b"ACK_CMD", addr)
                continue
            
            total_pkts += 1
            
            # Simulate packet loss
            if random.random() < current_loss_rate:
                dropped_pkts += 1
                continue

            try:
                seq_num_str, payload = msg.split('|', 1)
                seq_num = int(seq_num_str)
                
                if seq_num == expected_seq_num:
                    expected_seq_num += 1
                    total_received += len(payload)
                
                # Cumulative ACK
                ack = str(expected_seq_num - 1).encode()
                
                # Simulate return-way trip delay (RTT / 2)
                if current_rtt_s > 0:
                    time.sleep(current_rtt_s / 2.0)
                    
                sock.sendto(ack, addr)
                
                if payload == "EOF":
                    print(f"Run Complete. Recv: {total_received-3} bytes, Loss: {(dropped_pkts/total_pkts)*100:.2f}%")

            except Exception as e:
                print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nReceiver shutting down.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_receiver()
