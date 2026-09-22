# Subnet Ping Sweeper 📡

A high-speed active reconnaissance utility designed to discover live hosts across an IPv4 network segment. Built to demonstrate NOC troubleshooting workflows and SOC asset discovery methodologies.

**Features:**
* Utilizes Python's `ipaddress` library to calculate valid host ranges dynamically from CIDR notation.
* Implements `concurrent.futures.ThreadPoolExecutor` to ping up to 50 hosts simultaneously, reducing scan times for a /24 subnet from minutes to seconds.
* Automatically detects the host operating system (`platform`) to inject the correct OS-specific native ICMP parameters to minimize timeouts.
* Features a stylized GUI that remains fully responsive during deep network scans.

*Built as Day 12 of a 30-Day Network Engineering & Security portfolio streak.*
