import socket
import time
import threading

class Sender:
    def __init__(self, host='127.0.0.1', port=12345, window_size=5, timeout=0.5):
        self.host = host
        self.port = port
        self.window_size = window_size
        self.timeout = timeout
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1) # short timeout for non-blocking recv
        
        self.base = 0
        self.next_seq_num = 0
        self.packets = []
        self.timer_start_time = None
        self.lock = threading.Lock()
        self.running = True

    def create_packets(self, data, chunk_size=1024):
        self.packets = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            seq_num = len(self.packets)
            self.packets.append(f"{seq_num}|{chunk}")
        # Add EOF packet
        self.packets.append(f"{len(self.packets)}|EOF")

    def ack_listener(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                ack_num = int(data.decode())
                with self.lock:
                    if ack_num >= self.base:
                        print(f"ACK received: {ack_num}")
                        self.base = ack_num + 1
                        if self.base == self.next_seq_num:
                            self.timer_start_time = None # Stop timer
                        else:
                            self.timer_start_time = time.time() # Restart timer
            except (socket.timeout, ValueError):
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in ack_listener: {e}")

    def send_data(self):
        self.timer_start_time = None
        listener_thread = threading.Thread(target=self.ack_listener)
        listener_thread.start()

        start_time = time.time()
        total_data_sent = sum(len(p.split('|', 1)[1]) for p in self.packets if '|' in p)
        
        print(f"Starting transmission of {len(self.packets)} packets...")

        while self.base < len(self.packets):
            with self.lock:
                # Send packets within the window
                while self.next_seq_num < self.base + self.window_size and self.next_seq_num < len(self.packets):
                    pkt = self.packets[self.next_seq_num]
                    # print(f"Sending packet: {self.next_seq_num}")
                    self.sock.sendto(pkt.encode(), (self.host, self.port))
                    if self.base == self.next_seq_num:
                        self.timer_start_time = time.time()
                    self.next_seq_num += 1

                # Check for timeout
                if self.timer_start_time and (time.time() - self.timer_start_time > self.timeout):
                    print(f"Timeout! Retransmitting window from {self.base}")
                    self.timer_start_time = time.time()
                    for i in range(self.base, self.next_seq_num):
                        pkt = self.packets[i]
                        self.sock.sendto(pkt.encode(), (self.host, self.port))

            time.sleep(0.01) # Small sleep to avoid CPU pinning

        end_time = time.time()
        duration = end_time - start_time
        throughput = (total_data_sent * 8) / (duration * 1024) # kbps

        print("\n--- Sender Statistics ---")
        print(f"Total time: {duration:.2f} seconds")
        print(f"Effective throughput: {throughput:.2f} kbps")
        
        self.running = False
        listener_thread.join()
        self.sock.close()

if __name__ == "__main__":
    sender = Sender(window_size=10, timeout=0.3)
    # Generate some dummy data (100KB)
    data = "Hello Network! " * 6000 
    sender.create_packets(data)
    sender.send_data()
