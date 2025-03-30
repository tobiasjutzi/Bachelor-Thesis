@load base/protocols/conn

module Conn;

redef record Conn::Info {
    id_orig_h: addr;
    id_resp_h: addr;
};

event zeek_init() {
    Log::create_stream(Conn::LOG, [$columns=Info, $path="conn_custom"]);
}
