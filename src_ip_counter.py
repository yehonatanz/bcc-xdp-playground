import socket
import sys
import time
from contextlib import contextmanager
from typing import Iterator

from bcc import BPF
from bcc.table import HashTable


@contextmanager
def load_xdp_prog(
    interface: str,
    path: str = "src_ip_counter.c",
    name: str = "xdp_prog",
    map_name: str = "src_hist",
) -> Iterator[HashTable]:
    print("Compiling...")
    b = BPF(src_file=path)
    print("Verifying...")
    fn = b.load_func(name, b.XDP)
    src_hist = b.get_table(map_name)
    print("Attaching...")
    b.attach_xdp(interface, fn)
    print("Attached!")
    try:
        yield src_hist
    finally:
        print("Removing...")
        b.remove_xdp(interface)
        print("Removed!")


def int_to_ip(ip: int) -> str:
    return socket.inet_ntoa(ip.to_bytes(4, sys.byteorder))


def report_hist(hist: HashTable) -> None:
    for ip, count in hist.items():
        print(f"{int_to_ip(ip.value)}: {count.value}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <interface>", file=sys.stderr)
        sys.exit(1)
    interface = sys.argv[1]
    with load_xdp_prog(interface) as src_hist:
        while True:
            time.sleep(1)
            report_hist(src_hist)
            src_hist.clear()
            print("----------------")


if __name__ == "__main__":
    main()
