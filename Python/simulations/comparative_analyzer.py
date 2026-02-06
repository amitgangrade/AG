import socket
import time
import threading
import matplotlib.pyplot as plt

class BaseSender:
    def __init__(self, host='127.0.0.1', port=12345, timeout=0.2):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.05)
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
        self.packets.append(f"{len(self.packets)}|EOF")

class UDPSender(BaseSender):
    def __init__(self, window_size=10, **kwargs):
        super().__init__(**kwargs)
        self.window_size = window_size

    def ack_listener(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                ack_num = int(data.decode())
                with self.lock:
                    if ack_num >= self.base:
                        self.base = ack_num + 1
                        self.timer_start_time = time.time() if self.base != self.next_seq_num else None
            except: continue

class TCPSimSender(BaseSender):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cwnd = 1.0  # Congestion Window
        self.ssthresh = 64
        self.dup_acks = 0
        self.last_ack = -1

    def ack_listener(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                ack_num = int(data.decode())
                with self.lock:
                    if ack_num >= self.base:
                        if ack_num > self.last_ack:
                            # New ACK
                            if self.cwnd < self.ssthresh:
                                self.cwnd += 1  # Slow Start
                            else:
                                self.cwnd += 1.0 / int(self.cwnd)  # Congestion Avoidance
                            self.base = ack_num + 1
                            self.last_ack = ack_num
                            self.dup_acks = 0
                        else:
                            # Duplicate ACK
                            self.dup_acks += 1
                            if self.dup_acks == 3:
                                # Fast Retransmit
                                self.ssthresh = max(self.cwnd / 2, 2)
                                self.cwnd = self.ssthresh
                                self.next_seq_num = self.base  # Retransmit
                        
                        self.timer_start_time = time.time() if self.base != self.next_seq_num else None
            except: continue

def run_protocol_test(sender_class, loss_rate, data_size_kb, name):
    sender = sender_class(host='127.0.0.1', port=12345)
    data = "X" * (data_size_kb * 1024)
    sender.create_packets(data)
    
    # Handshake to set loss rate
    sender.sock.sendto(f"CMD:SET_LOSS:{loss_rate}".encode(), (sender.host, sender.port))
    time.sleep(1.0)

    listener = threading.Thread(target=sender.ack_listener)
    listener.start()
    
    start_time = time.time()
    while sender.base < len(sender.packets):
        with sender.lock:
            limit = sender.window_size if hasattr(sender, 'window_size') else int(sender.cwnd)
            while sender.next_seq_num < sender.base + limit and sender.next_seq_num < len(sender.packets):
                sender.sock.sendto(sender.packets[sender.next_seq_num].encode(), (sender.host, sender.port))
                if sender.base == sender.next_seq_num: sender.timer_start_time = time.time()
                sender.next_seq_num += 1
                time.sleep(0.001)

            if sender.timer_start_time and (time.time() - sender.timer_start_time > sender.timeout):
                # Timeout
                if hasattr(sender, 'cwnd'):
                    sender.ssthresh = max(sender.cwnd / 2, 2)
                    sender.cwnd = 1.0
                sender.next_seq_num = sender.base
                sender.timer_start_time = time.time()
        time.sleep(0.01)

    duration = time.time() - start_time
    sender.running = False
    listener.join()
    sender.sock.close()
    return (len(data) * 8) / duration

if __name__ == "__main__":
    loss_rates = [0, 0.01, 0.05, 0.10, 0.20, 0.50, 0.70]
    data_size = 128 # 128KB for reasonable speed
    
    udp_results = []
    tcp_results = []

    print(f"{'Loss %':<10} | {'UDP (bps)':<15} | {'TCP-Sim (bps)':<15}")
    print("-" * 45)

    for loss in loss_rates:
        udp_bps = run_protocol_test(UDPSender, loss, data_size, "UDP")
        tcp_bps = run_protocol_test(TCPSimSender, loss, data_size, "TCP-Sim")
        
        udp_results.append(udp_bps)
        tcp_results.append(tcp_bps)
        
        print(f"{loss*100:<10.1f} | {udp_bps:<15.2f} | {tcp_bps:<15.2f}")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot([l*100 for l in loss_rates], udp_results, marker='o', label='UDP (Go-Back-N)')
    plt.plot([l*100 for l in loss_rates], tcp_results, marker='s', label='TCP-Sim (AIMD/Reno)')
    plt.title('Protocol Comparison: Throughput vs. Packet Loss')
    plt.xlabel('Packet Loss Rate (%)')
    plt.ylabel('Throughput (bits per second)')
    plt.legend()
    plt.grid(True)
    plt.savefig('protocol_comparison_plot.png')
    print("\nComparison plot saved as 'protocol_comparison_plot.png'")
