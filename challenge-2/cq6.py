import pyshark
from utils import extract_dns_ips

PCAP_FILE = "challenge-2/challenge2.pcapng"
HOSTNAME = "test.mosquitto.org"


def main():
    ips = extract_dns_ips(PCAP_FILE, HOSTNAME)
    mqqt_public_messages = find_mqtt_public_messages(PCAP_FILE, ips)
    print(f"Number of MQTT public messages: {len(mqqt_public_messages)}")


def find_mqtt_public_messages(pcap_file, ips):
    capture = pyshark.FileCapture(pcap_file, display_filter="mqtt")
    mqtt_public_messages = []

    for packet in capture:
        mqtt_msgtype = packet.mqtt.get("mqtt.msgtype")
        mqtt_qos = packet.mqtt.get("mqtt.qos", "-1")
        mqtt_retain = packet.mqtt.get("mqtt.retain", "False")
        ip_dst = packet.ip.dst if hasattr(packet, "ip") else packet.ipv6.dst

        if (
            mqtt_msgtype == "3"
            and mqtt_qos == "0"
            and mqtt_retain == "True"
            and ip_dst in ips
        ):
            mqtt_public_messages.append(packet)

    capture.close()
    return mqtt_public_messages


if __name__ == "__main__":
    main()
