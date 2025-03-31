import pyshark


def extract_dns_ips(capture, hostname) -> list[str]:
    capture = pyshark.FileCapture(capture, display_filter="dns")
    dns_ips = set()
    for packet in capture:
        if (
            hasattr(packet, "dns")
            and packet.dns.get("dns.resp.name") == hostname
            and (hasattr(packet.dns, "a") or hasattr(packet.dns, "aaaa"))
        ):
            if hasattr(packet.dns, "a"):
                [dns_ips.add(ip.get_default_value()) for ip in packet.dns.a.all_fields]
            if hasattr(packet.dns, "aaaa"):
                [
                    dns_ips.add(ip.get_default_value())
                    for ip in packet.dns.aaaa.all_fields
                ]

    capture.close()
    return dns_ips
