import pyshark


def main():
    pcap_file = "challenge-2/challenge2.pcapng"

    print("Resolved IP addresses")
    for host in ["coap.me", "broker.hivemq.com", "test.mosquitto.org"]:
        ips = extract_dns_ips(pcap_file, host)
        print(f"{host}:")
        if ips[0]:
            print(f"\t{", ".join(ips[0])} (IPv4)")
        if ips[1]:
            # Allign with length of hostname + ": "
            print(f"\t{", ".join(ips[1])} (IPv6)")

    print("\nChallenge Question solutions")
    print("cq1", cq1(pcap_file), sep="\t")
    print("cq2", cq2(pcap_file), sep="\t")
    print("cq3", cq3(pcap_file), sep="\t")
    print("cq4", cq4(pcap_file), sep="\t")
    print("cq5", cq5(pcap_file), sep="\t")
    print("cq6", cq6(pcap_file), sep="\t")
    print("cq7", cq7(pcap_file), sep="\t")


def cq1(pcap_file) -> int:
    # Open the .pcapng file with pyshark and store it in a variable filtered by coap packages
    capture = pyshark.FileCapture(pcap_file, display_filter="coap")

    confirmable_put_tokens = []  # Store tokens of Confirmable PUT requests
    unsuccessful_responses_count = 0

    # Find all Confirmable PUT requests and store their tokens
    for packet in capture:
        if hasattr(packet, "coap"):
            coap_type = int(packet.coap.get("coap.type"))
            coap_code = int(packet.coap.get("coap.code"))
            coap_token = packet.coap.get("coap.token")

            # Check if it is a Confirmable PUT request (coap.type = 0, coap.code = 3)
            if coap_type == 0 and coap_code == 3:
                if coap_token not in confirmable_put_tokens:
                    confirmable_put_tokens.append(coap_token)

    # Find the responses to the unique tokens and check if any have coap.code >= 128
    # Coap packets with coap.code >= 128 are error response packets, like 4.xx and 5.xx
    capture.close()
    capture = pyshark.FileCapture(pcap_file, display_filter="coap")

    for packet in capture:
        if hasattr(packet, "coap"):
            coap_code = int(packet.coap.get("coap.code"))
            coap_token = packet.coap.get("coap.token")
            ip_src = packet.ip.src

            # If the token is one of the Confirmable PUT requests, it is an error response (coap_code >= 128) AND from the local CoAP server (ip.src = 127.0.0.1)
            if (
                coap_token in confirmable_put_tokens
                and coap_code >= 128
                and ip_src == "127.0.0.1"
            ):
                confirmable_put_tokens.remove(coap_token)
                unsuccessful_responses_count += 1

    capture.close()

    return unsuccessful_responses_count


def cq2(pcap_file) -> int:
    display_filter = (
        "coap "  # Filter for COAP packets
        "and coap.code == 1 "  # Get requests
        "and ip.addr == 134.102.218.18"  # coap.me ip address
    )
    capture = pyshark.FileCapture(pcap_file, display_filter=display_filter)
    resources = {}
    for packet in capture:
        # Collect COAP fields
        coap_type = int(packet.coap.get("coap.type"))
        coap_token = packet.coap.get("coap.token")
        coap_resource = packet.coap.get("coap.opt.uri_path")

        # For each resource track the tokens of the requests
        if not coap_resource in resources:
            resources[coap_resource] = (set(), set())  # (confirmable, non-confirmable)

        if coap_type == 0:  # Confirmable
            resources[coap_resource][0].add(coap_token)

        if coap_type == 1:  # Non-confirmable
            resources[coap_resource][1].add(coap_token)
    capture.close()

    filtered_resources = {
        key: value
        for key, value in resources.items()
        if (len(value[0]) == len(value[1]))
    }  # Filter resources with equal number of confirmable and non-confirmable tokens

    # Get the number of resources
    return len(filtered_resources)


def cq3(pcap_file) -> int:
    display_filter = (
        "mqtt "  # Filter for MQTT packets
        "and mqtt.msgtype == 8 "  # Subscribe packets
        "and mqtt.topic contains '#' "  # wildcard topics
        "and ip.dst in {18.192.151.104, 35.158.43.69, 35.158.34.213}"  # test.mosquitto.org ip addresses
    )
    capture = pyshark.FileCapture(pcap_file, display_filter=display_filter)
    mqtt_subscribers = [packet for packet in capture]
    capture.close()

    # Get the number of unique subscribers
    return len(get_packet_endpoints(mqtt_subscribers, unique=True))


def cq4(pcap_file) -> int:
    display_filter = "mqtt and mqtt.willtopic[:10] == university"  # last will topic starts with "university"
    capture = pyshark.FileCapture(pcap_file, display_filter=display_filter)
    mqtt_will = [packet for packet in capture]
    capture.close()

    # Get the number of unique last will recipients
    return len(get_packet_endpoints(mqtt_will, unique=True))


def cq5(pcap_file) -> int:
    capture = pyshark.FileCapture(pcap_file, display_filter="mqtt")

    last_wills = []
    all_messages = []
    sub_requests = []

    for packet in capture:
        """
        Iterate through the packets and categorize them based on MQTT message types.
        """

        # Extract source and destination information
        src = get_packet_endpoint(packet)
        dst = get_packet_endpoint(packet, destination=True)

        # Extract MQTT fields
        mqtt_willtopic = packet.mqtt.get("mqtt.willtopic")
        mqtt_willmsg = packet.mqtt.get("mqtt.willmsg")
        mqtt_msg = packet.mqtt.get("mqtt.msg")
        mqtt_topic = packet.mqtt.get("mqtt.topic")
        mqtt_msgtype = packet.mqtt.get("mqtt.msgtype")

        # Find Connect packets with a last will
        if mqtt_willtopic:
            last_wills.append((mqtt_willtopic, mqtt_willmsg))

        # Find Subscribe packets without wildcards
        if mqtt_msgtype == "8" and not any(char in mqtt_topic for char in ["#", "+"]):
            sub_requests.append((mqtt_topic, src))  # (topic, subscriber)

        # Find Publish packets
        if mqtt_msgtype == "3":
            all_messages.append(
                {
                    "topic": mqtt_topic,  # Topic of the message
                    "msg": mqtt_msg,  # Message content
                    "dst": dst,  # Message recipient
                }
            )
    capture.close()

    # Find number of messages matching last wills and subscriptions without wildcards
    return sum(
        1
        for message in all_messages
        if (message["topic"], message["msg"]) in last_wills
        and (message["topic"], message["dst"]) in sub_requests
    )


def cq6(pcap_file) -> int:
    display_filter = (
        "mqtt "  # Filter for MQTT packets
        "and mqtt.msgtype == 3 "  # Publish message packets
        "and mqtt.qos == 0 "  # QoS level 0
        "and mqtt.retain == True "  # Retained messages
        "and (ip.dst in {5.196.78.28} "  # test.mosquitto.org ip address
        "or ipv6.dst in {2001:41d0:a:6f1c::1})"  # test.mosquitto.org IPv6 address
    )
    capture = pyshark.FileCapture(pcap_file, display_filter=display_filter)
    mqtt_public_messages = [packet for packet in capture]
    capture.close()

    return len(mqtt_public_messages)


def cq7(pcap_file) -> int:
    display_filter = (
        "udp.port == 1885 or tcp.port == 1885"  # Search for any packet on port 1885
    )
    # We find zero packets, so no reason to construct a more complex filter
    capture = pyshark.FileCapture(pcap_file, display_filter=display_filter)
    mqttsn_messages = [packet for packet in capture]
    capture.close()

    return len(mqttsn_messages)


## Helper functions ---------------------------------------------------------------------


def get_packet_endpoints(
    packets,
    destination=False,
    unique=False,
):
    endpoints = [get_packet_endpoint(packet, destination) for packet in packets]
    return list(set(endpoints)) if unique else endpoints


def get_packet_endpoint(packet, destination=False):
    # get the ip and port from the packet, either source or destination
    ip_field, port_field = None, None

    # Extract IP address (IPv4 or IPv6)
    if hasattr(packet, "ip"):
        ip_field = packet.ip.dst if destination else packet.ip.src
    elif hasattr(packet, "ipv6"):
        ip_field = f"[{packet.ipv6.dst}]" if destination else f"[{packet.ipv6.src}]"

    # Extract port (TCP or UDP)
    if hasattr(packet, "tcp"):
        port_field = packet.tcp.dstport if destination else packet.tcp.srcport
    elif hasattr(packet, "udp"):
        port_field = packet.udp.dstport if destination else packet.udp.srcport

    # If no IP address is found, return "Unknown"
    if ip_field is None:
        return "Unknown"

    # Return formatted endpoint string
    return f"{ip_field}:{port_field}" if port_field else ip_field


def extract_dns_ips(capture, hostname):
    display_filter = "dns and dns.qry.name == " + hostname
    capture = pyshark.FileCapture(capture, display_filter=display_filter)
    ipv4, ipv6 = set(), set()
    for packet in capture:
        if hasattr(packet.dns, "a"):
            [ipv4.add(ip.get_default_value()) for ip in packet.dns.a.all_fields]
        if hasattr(packet.dns, "aaaa"):
            [ipv6.add(ip.get_default_value()) for ip in packet.dns.aaaa.all_fields]

    capture.close()
    return (list(ipv4), list(ipv6))


if __name__ == "__main__":
    main()
