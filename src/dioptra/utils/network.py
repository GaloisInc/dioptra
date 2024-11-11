class NetworkModel:
    def __init__(
        self, send_bits_per_second: int, recv_bits_per_second: int, latency: int
    ):
        self.send_bits_per_second = send_bits_per_second
        self.recv_bits_per_second = recv_bits_per_second
        self.latency = latency

    def send_latency_ns(self, bytes: int) -> int:
        return self.latency + (bytes * 8 * 10**9) // self.send_bits_per_second

    def recv_latency_ns(self, bytes: int) -> int:
        return self.latency + (bytes * 8 * 10**9) // self.recv_bits_per_second
