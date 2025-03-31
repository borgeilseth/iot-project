def unique_clients(packets):
    unique_clients = set()
    for packet in packets:
        ip_src = packet.ip.src if hasattr(packet, "ip") else packet.ipv6.src
        is_ipv6 = hasattr(packet, "ipv6")
        tcp_src = packet.tcp.srcport
        if ip_src:
            if is_ipv6:
                unique_clients.add(f"[{ip_src}]:{tcp_src}")
            else:
                unique_clients.add(f"{ip_src}:{tcp_src}")
    return unique_clients
