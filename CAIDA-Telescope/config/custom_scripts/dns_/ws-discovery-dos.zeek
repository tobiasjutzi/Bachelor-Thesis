module DoS;

@load-sigs /home/tobias/work/Cloud-Telescope/shell/config/custom_scripts/dns-amplification/ws-discovery-dos.sig

# file containing signature
#redef signature_files += "ws-discovery-dos.sig";

redef enum Notice::Type += {
	## Indicates a high likelyhood of successful shellshock exploitation.
       	WS_Discovery_Attempt,
       	SourceList,
};

redef Signatures::actions += {
        ["ws-discovery-udp"] = Signatures::SIG_ALARM_PER_ORIG,
        ["ws-faultstring-udp"] = Signatures::SIG_COUNT_PER_RESP,
};


export {
	global expire_dos_victim: function(t: table[addr] of set[addr], idx: addr): interval &redef;
	global dos_victim: table[addr] of set[addr] &create_expire=3 mins &expire_func=expire_dos_victim ;
}


hook Notice::policy(n: Notice::Info)
	{
  	if ( n$note == DoS::SourceList)
        {
            add n$actions[Notice::ACTION_EMAIL ];
        }
	}

function expire_dos_victim(t: table[addr] of set[addr], idx: addr): interval
	{

	local _msg = "" ;
	for (a in t)
	   for (b in t[a])
		_msg += fmt(" %s ", b);

	if (|t[idx]| > 0) {
		NOTICE([$note=DoS::SourceList, $src=idx,
			$msg=fmt("Dos Victim: %s - Sources : [%s]", idx, _msg)]);
	}
	return 0 secs ;
	}

event signature_match(state: signature_state, msg: string, data: string)
	{
    local resp = state$conn$id$resp_h ;
    local orig = state$conn$id$orig_h;

    if (/ws-discovery-udp/ in state$sig_id) {

		if (orig !in dos_victim) {
			local a: set[addr] ;
			dos_victim[orig]=a ;
		}
	}

    if (/^ws-faultstring-udp$/ in state$sig_id){

		if (orig in dos_victim) {
		   add dos_victim[orig][resp] ;
		}
	}

	}