signature ws-discovery-udp {
    ip-proto == udp
    dst-port == 3702
    payload /\x3c\xaa\x3e|\x3c\x3a\x3e|\x3c\x2e\x3e/
    event "ws-discovery-dos"
}

signature ws-faultstring-udp {
    ip-proto == udp
    requires-reverse-signature ws-discovery-udp
    src-port == 3702
    #payload /<SOAP-ENV:|xml:version/
    event "ws-discovery-dos-faultstring"
}

#payload /\<SOAP-ENV\:Fault/
#payload /\x3c\x53\x4f\x41\x50\x2d\x45\x4e\x56\x3a\x46\x61\x75\x6c\x74/