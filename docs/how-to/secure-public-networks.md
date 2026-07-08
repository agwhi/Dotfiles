# Secure Public Networks

Protect privacy and traffic on untrusted Wi-Fi (cafés, airports, hotels,
conferences). The tools install with `just bootstrap`; their configs are
applied by `just link`. VPN account, browser, and firewall settings need the
one-time manual steps below.

## Quick use

```bash
secure-on    # Enable DNS encryption + VPN
secure-off   # Disable both when back on a trusted network
dns-test     # Open a DNS leak test; expect encrypted resolvers, not your ISP
```

Enable on any untrusted network or when handling sensitive data. Disable at
home/office or when the VPN gets in the way; individual pieces are available
as `dns-start`/`dns-stop` and `vpn-on`/`vpn-off`.

## What each tool does

| Tool | Purpose | Managed piece |
| --- | --- | --- |
| dnscrypt-proxy | Encrypted DNS (Cloudflare/Quad9, DNSSEC) | repo config, linked into `~/.config` |
| NordVPN | Encrypts all traffic, hides IP | Homebrew cask; account is manual |
| LuLu | Blocks unknown outbound connections | Homebrew formula; `lulu-backup` for rules |
| Brave | Private browsing (Shields, anti-fingerprinting) | Homebrew cask; settings are manual |

## One-time manual configuration

### NordVPN

Open the app once and sign in; `vpn-on`/`vpn-off` use the `nordvpn` CLI after
that.

### Brave

1. Open `brave://settings/shields/` and enable: block trackers & ads,
   block fingerprinting, block social media trackers.
2. Open `brave://settings/privacy/` and set WebRTC IP handling to
   "Disable non-proxied UDP"; disable payment method checks.

### LuLu

1. Open LuLu preferences.
2. Enable "Automatically allow signed applications".
3. Set unknown applications to "Ask user".
4. Back up rules with `lulu-backup` (restore with `lulu-restore`,
   list with `lulu-list`).

### macOS hardening for public networks

1. Wi-Fi: uncheck "Remember networks this computer has joined" and
   "Ask to join new networks".
2. Sharing: disable all services; turn off AirDrop in Control Center.
3. Firewall: enable and set to "Block all incoming connections".

## Troubleshooting

```bash
# DNS
brew services list | grep dnscrypt-proxy   # Is the service running?
dns-stop && dns-start                      # Restart DNS encryption
nslookup google.com 127.0.0.1              # Test local resolution

# VPN
nordvpn status
vpn-off && vpn-on
```

Performance expectations: DNS encryption costs ~1–5 ms; the VPN costs
10–50 ms latency and some bandwidth. Combined they are the best protection at
a moderate performance cost.
