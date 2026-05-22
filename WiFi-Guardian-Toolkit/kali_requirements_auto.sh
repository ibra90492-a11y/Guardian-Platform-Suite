#!/usr/bin/env bash
touch /root/.hushlogin 2>/dev/null || true
if id -u kali >/dev/null 2>&1; then
    touch /home/kali/.hushlogin
fi
export DEBIAN_FRONTEND=noninteractive

echo '=== Kali Requirements Auto Installer ==='

echo '[1/5] apt update -y'
apt update -y

echo '[2/5] Installing base tools: net-tools curl macchanger tor torsocks netcat-traditional'
apt install -y net-tools curl macchanger tor torsocks netcat-traditional || true

echo '[3/5] Installing network & wireless tools: nmap masscan tcpdump aircrack-ng wifite reaver'
apt install -y nmap masscan tcpdump aircrack-ng wifite reaver || true

echo '[4/5] Installing password & web tools: john hashcat hydra crunch sqlmap nikto gobuster whatweb wpscan medusa'
apt install -y john hashcat hydra crunch sqlmap nikto gobuster whatweb wpscan medusa || true

echo '[5/5] Installing forensics tools: binwalk foremost python3-pip'
apt install -y binwalk foremost python3-pip || true

if command -v vol >/dev/null 2>&1; then
    echo '[INFO] Volatility is already available.'
elif apt-cache show volatility3 >/dev/null 2>&1; then
    echo '[INFO] Installing Volatility 3 from apt.'
    apt install -y volatility3 || true
else
    echo '[INFO] volatility3 package is not available in apt. Trying pip install...'
    python3 -m pip install --break-system-packages -U volatility3 || true
fi

if command -v vol >/dev/null 2>&1; then
    echo '[OK] Volatility command available: vol'
else
    echo '[WARN] Volatility was not installed automatically. You can retry later with:'
    echo '       python3 -m pip install --break-system-packages -U volatility3'
fi

echo ''
echo '=== All done! ==='
echo 'To install the full Kali suite later: apt install -y kali-linux-large'
echo 'Terminal will remain open.'
exec bash
