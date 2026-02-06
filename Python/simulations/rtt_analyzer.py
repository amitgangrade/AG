import socket
import time
import threading
import matplotlib.pyplot as plt

# Reuse the protocol logic from comparative_analyzer.py
# (For a real system we'd import, but for simplicity in a single script:)

class BaseSender:
    def __init__(self, host='127.0.0.1', port=12345, timeout_mult=2.5):
        self.host = host
        self.port = port
        self.timeout_mult = timeout_mult
        self.timeout = 0.5  # Default
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
        self.cwnd = 1.0
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
                            if self.cwnd < self.ssthresh: self.cwnd += 1
                            else: self.cwnd += 1.0 / int(self.cwnd)
                            self.base = ack_num + 1
                            self.last_ack = ack_num
                            self.dup_acks = 0
                        else:
                            self.dup_acks += 1
                            if self.dup_acks == 3:
                                self.ssthresh = max(self.cwnd / 2, 2)
                                self.cwnd = self.ssthresh
                                self.next_seq_num = self.base
                        
                        self.timer_start_time = time.time() if self.base != self.next_seq_num else None
            except: continue

def run_rtt_test(sender_class, rtt_ms, loss_rate, data_size_kb):
    sender = sender_class(host='127.0.0.1', port=12345)
    # RTT-Aware Timeout: timeout should be larger than RTT
    sender.timeout = max(0.001, (rtt_ms / 1000.0) * sender.timeout_mult)
    
    data = "Y" * (data_size_kb * 1024)
    sender.create_packets(data)
    
    # Handshake to set RTT and Loss
    sender.sock.sendto(f"CMD:SET_RTT:{rtt_ms}".encode(), (sender.host, sender.port))
    time.sleep(0.5)
    sender.sock.sendto(f"CMD:SET_LOSS:{loss_rate}".encode(), (sender.host, sender.port))
    time.sleep(0.5)

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
                # No extra sleep here to let RTT be the limiting factor

            if sender.timer_start_time and (time.time() - sender.timer_start_time > sender.timeout):
                if hasattr(sender, 'cwnd'):
                    sender.ssthresh = max(sender.cwnd / 2, 2)
                    sender.cwnd = 1.0
                sender.next_seq_num = sender.base
                sender.timer_start_time = time.time()
        time.sleep(0.001)

    duration = time.time() - start_time
    sender.running = False
    listener.join()
    sender.sock.close()
    return (len(data) * 8) / duration

if __name__ == "__main__":
    rtts = [0.1, 1.0, 10, 100, 500] # ms
    fixed_loss = 0.01 # 1% loss
    data_size = 32 # 32KB to make high-latency runs finish faster
    
    udp_results = []
    tcp_results = []

    print(f"RTT Analysis (Loss={fixed_loss*100}% on 32KB payload)")
    print(f"{'RTT (ms)':<10} | {'UDP (bps)':<15} | {'TCP-Sim (bps)':<15}")
    print("-" * 45)

    for rtt in rtts:
        print(f"Testing RTT={rtt}ms...")
        udp_bps = run_rtt_test(UDPSender, rtt, fixed_loss, data_size)
        print(f"  UDP: {udp_bps:.2f} bps")
        tcp_bps = run_rtt_test(TCPSimSender, rtt, fixed_loss, data_size)
        print(f"  TCP: {tcp_bps:.2f} bps")
        
        udp_results.append(udp_bps)
        tcp_results.append(tcp_bps)
        
        print(f"{rtt:<10.1f} | {udp_bps:<15.2f} | {tcp_bps:<15.2f}")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(rtts, udp_results, marker='o', label='UDP (Go-Back-N)')
    plt.plot(rtts, tcp_results, marker='s', label='TCP-Sim (AIMD/Reno)')
    plt.xscale('log') # Log scale for RTT since it spans orders of magnitude
    plt.title(f'Protocol Throughput vs. Latency (RTT) at {fixed_loss*100}% Loss')
    plt.xlabel('Round Trip Time (ms) - Log Scale')
    plt.ylabel('Throughput (bits per second)')
    plt.legend()
    plt.grid(True, which="both", ls="-")
    plt.savefig('rtt_impact_plot.png')
    print("\nRTT impact plot saved as 'rtt_impact_plot.png'")
