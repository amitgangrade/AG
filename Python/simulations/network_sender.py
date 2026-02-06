import socket
import time
import threading
import matplotlib.pyplot as plt

class NetworkSender:
    def __init__(self, host='127.0.0.1', port=12345, window_size=10, timeout=0.2):
        self.host = host
        self.port = port
        self.window_size = window_size
        self.timeout = timeout
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        
        self.base = 0
        self.next_seq_num = 0
        self.packets = []
        self.timer_start_time = None
        self.lock = threading.Lock()
        self.running = True
        self.results = []

    def create_packets(self, data, chunk_size=1024):
        self.packets = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            seq_num = len(self.packets)
            self.packets.append(f"{seq_num}|{chunk}")
        self.packets.append(f"{len(self.packets)}|EOF")

    def ack_listener(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                ack_num = int(data.decode())
                with self.lock:
                    if ack_num >= self.base:
                        self.base = ack_num + 1
                        if self.base == self.next_seq_num:
                            self.timer_start_time = None
                        else:
                            self.timer_start_time = time.time()
            except:
                continue

    def run_simulation(self, data_size_kb, loss_rates):
        data = "A" * (data_size_kb * 1024)
        self.create_packets(data)
        
        total_data_bits = len(data) * 8

        for loss in loss_rates:
            print(f"\n>>> Running test for {loss*100}% loss...")
            # Set loss rate on receiver
            self.sock.sendto(f"CMD:SET_LOSS:{loss}".encode(), (self.host, self.port))
            time.sleep(1.0) # Wait for receiver to sync

            self.base = 0
            self.next_seq_num = 0
            self.running = True
            
            listener_thread = threading.Thread(target=self.ack_listener)
            listener_thread.start()

            start_time = time.time()
            
            while self.base < len(self.packets):
                with self.lock:
                    while self.next_seq_num < self.base + self.window_size and self.next_seq_num < len(self.packets):
                        pkt = self.packets[self.next_seq_num]
                        self.sock.sendto(pkt.encode(), (self.host, self.port))
                        if self.base == self.next_seq_num:
                            self.timer_start_time = time.time()
                        self.next_seq_num += 1
                        # Small delay to prevent local socket buffer overflow
                        time.sleep(0.005)

                    if self.timer_start_time and (time.time() - self.timer_start_time > self.timeout):
                        print(f"    Timeout! Retransmitting from {self.base}")
                        self.timer_start_time = time.time()
                        for i in range(self.base, self.next_seq_num):
                            self.sock.sendto(self.packets[i].encode(), (self.host, self.port))
                
                if self.base % 50 == 0:
                    print(f"    Progress: {self.base}/{len(self.packets)} packets ACKed")
                
                time.sleep(0.01)

            duration = time.time() - start_time
            bps = total_data_bits / duration
            self.results.append((loss * 100, bps))
            
            self.running = False
            listener_thread.join()
            print(f"Done. Throughput: {bps:.2f} bits/sec")

        self.display_results()
        self.plot_results()

    def display_results(self):
        print("\n" + "="*45)
        print(f"{'Packet Loss (%)':<20} | {'Throughput (bits/sec)':<20}")
        print("-" * 45)
        for loss, bps in self.results:
            print(f"{loss:<20.1f} | {bps:<20.2f}")
        print("="*45 + "\n")

    def plot_results(self):
        losses = [r[0] for r in self.results]
        bps_values = [r[1] for r in self.results]
        
        plt.figure(figsize=(10, 6))
        plt.plot(losses, bps_values, marker='o', linestyle='-', color='b')
        plt.title('Network Throughput vs. Packet Loss Rate')
        plt.xlabel('Packet Loss Rate (%)')
        plt.ylabel('Transmission Rate (bits per second)')
        plt.grid(True)
        plt.savefig('throughput_plot.png')
        print("Plot saved as 'throughput_plot.png'")

if __name__ == "__main__":
    sender = NetworkSender(window_size=10, timeout=0.2)
    loss_rates_to_test = [0, 0.01, 0.05, 0.10, 0.50, 0.90]
    # Use 500KB to make it reasonably fast but stable
    sender.run_simulation(data_size_kb=500, loss_rates=loss_rates_to_test)
