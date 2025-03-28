import pyshark

def find_unsuccessful_coap_put_requests(pcap_file):
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
    print("Number of different Confirmable PUT requests: ", len(confirmable_put_tokens))

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
            if coap_token in confirmable_put_tokens and coap_code >= 128 and ip_src == "127.0.0.1":
                confirmable_put_tokens.remove(coap_token)
                unsuccessful_responses_count += 1

    print(f"RESULT: \nNumber of different Confirmable PUT requests with unsuccessful responses: {unsuccessful_responses_count}")

pcap_file = "challenge2.pcapng"
find_unsuccessful_coap_put_requests(pcap_file)