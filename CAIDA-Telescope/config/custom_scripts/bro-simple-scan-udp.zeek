@load base/frameworks/notice
@load base/utils/time

module Scan;

export {
    redef enum Notice::Type += {
        UDP_Address_Scan,
        UDP_Port_Scan,
        UDP_Random_Scan,
    };

    type Attempt: record {
        victim: addr;
        scanned_port: port;
    };

    type Scan_Info: record {
        first_seen: time;
        attempts: set[Attempt];
        port_counts: table[port] of count;
    };

    const scan_timeout = 5min &redef;
    const scan_threshold = 3 &redef;

    global scan_attempt: event(scanner: addr, attempt: Attempt);
    global attacks: table[addr] of Scan_Info &read_expire=scan_timeout &redef;
}

function analyze_udp_scan(attempts: set[Attempt]): Notice::Info
{
    local ports: set[port];
    local victims: set[addr];

    for (a in attempts) {
        add victims[a$victim];
        add ports[a$scanned_port];
    }

    if (|ports| == 1) {
        for (p in ports) {
            return [$note=UDP_Address_Scan, $msg=fmt("UDP: %s unique hosts on port %s", |victims|, p), $p=p];
        }
    }
    if (|victims| == 1) {
        for (v in victims) {
            return [$note=UDP_Port_Scan, $msg=fmt("UDP: %s unique ports on host %s", |ports|, v)];
        }
    }
    return [$note=UDP_Random_Scan, $msg=fmt("UDP: %d hosts on %d ports", |victims|, |ports|)];
}

function add_udp_scan_attempt(scanner: addr, attempt: Attempt)
{
    if (scanner in attacks) {
        local si = attacks[scanner];
        add si$attempts[attempt];
    } else {
        local attempts: set[Attempt] = set();
        add attempts[attempt];
        attacks[scanner] = Scan_Info($first_seen=network_time(), $attempts=attempts, $port_counts=table());
    }

    if (|attacks[scanner]$attempts| >= scan_threshold) {
        NOTICE(analyze_udp_scan(attacks[scanner]$attempts));
        delete attacks[scanner];
    }
}

# UDP-Anfragen erfassen
event udp_request(c: connection)
{
    local scanner = c$id$orig_h;
    local victim = c$id$resp_h;
    local scanned_port = c$id$resp_p;
    add_udp_scan_attempt(scanner, Attempt($victim=victim, $scanned_port=scanned_port));
}

# ICMP Port Unreachable als Indikator für geschlossene UDP-Ports
event icmp_sent(c: connection, icmp_type: count, icmp_code: count, msg: string)
{
    if (icmp_type == 3 && icmp_code == 3) {
        local scanner = c$id$resp_h; # Die ursprüngliche Quelle der UDP-Anfrage
        local victim = c$id$orig_h;
        local scanned_port = c$id$orig_p;
        add_udp_scan_attempt(scanner, Attempt($victim=victim, $scanned_port=scanned_port));
    }
}
