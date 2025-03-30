import pandas as pd
from scapy.all import IP, UDP, DNS, DNSQR, DNSRR, wrpcap
from src.d01_data.read_files import read_log_file
from src.d01_data.log_names_enum import LogNamesEnum

def pcap():
        # Daten für die DNS-Anfrage
        client_ip = "104.248.118.173"
        server_ip = "188.226.134.9"
        query_name = "example.fake"
        resolved_ip = "93.184.216.34"

        # DNS-Anfrage erstellen
        dns_request = (
                IP(src=client_ip, dst=server_ip) /
                UDP(sport=12345, dport=53) /
                DNS(rd=1, qd=DNSQR(qname=query_name))
        )

        # DNS-Antwort erstellen
        dns_response = (
                IP(src=server_ip, dst=client_ip) /
                UDP(sport=53, dport=12345) /
                DNS(
                        id=dns_request[DNS].id,
                        qr=1,  # Antwort
                        aa=1,  # Authoritative Answer
                        qd=dns_request[DNS].qd,
                        an=DNSRR(rrname=query_name, ttl=300, rdata=resolved_ip)
                )
        )

        # Pakete in .pcap-Dateien speichern
        wrpcap("request.pcap", dns_request)
        wrpcap("response.pcap", dns_response)

        print("Die .pcap-Dateien wurden erstellt: 'request.pcap' und 'response.pcap'")


def backscatter() -> pd.DataFrame:
        conn1 = read_log_file(LogNamesEnum.conn, 'backscatterTest')
        return conn1


def test_import():
    import pandas as pd