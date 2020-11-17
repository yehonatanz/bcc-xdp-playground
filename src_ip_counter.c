#include <bcc/proto.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

BPF_HASH(src_hist, uint32_t, uint64_t, (1 << 20));

int xdp_prog(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    uint64_t len = 0;
    struct ethhdr *eth = data;
    len += sizeof(struct ethhdr);
    if (data + len > data_end) {
        return XDP_PASS;
    }
    if (eth->h_proto != ntohs(ETH_P_IP)) {
        return XDP_PASS;
    }
    struct iphdr *ip = data + len;
    len += sizeof(struct iphdr);
    if (data + len > data_end) {
        return XDP_PASS;
    }
    uint64_t zero = 0;
    uint64_t *count = src_hist.lookup_or_init(&ip->saddr, &zero);
    if (count) {
        ++*count;
    }
    return XDP_PASS;
}
