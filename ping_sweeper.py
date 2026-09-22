import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress
import subprocess
import platform
import threading
from concurrent.futures import ThreadPoolExecutor

# Global control flag
is_sweeping = False

def ping_host(ip_str):
    if not is_sweeping:
        return ip_str, False
        
    # Set OS-specific ping flags to ensure fast timeouts
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_flag = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_val = '1000' if platform.system().lower() == 'windows' else '1'
    
    command = ['ping', param, '1', timeout_flag, timeout_val, ip_str]
    
    try:
        # Hide the console window on Windows
        startupinfo = None
        if platform.system().lower() == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        
        if output.returncode == 0:
            return ip_str, True
        return ip_str, False
    except Exception:
        return ip_str, False

def run_sweep():
    global is_sweeping
    network_input = entry_subnet.get().strip()
    
    try:
        # strict=False allows user to input 192.168.1.50/24 and auto-correct to the base network
        network = ipaddress.ip_network(network_input, strict=False)
    except ValueError:
        messagebox.showerror("Invalid Subnet", "Please enter a valid CIDR network (e.g., 192.168.1.0/24)")
        reset_ui()
        return

    text_log.config(state=tk.NORMAL)
    text_log.delete(1.0, tk.END)
    text_log.insert(tk.END, f"[*] Starting Ping Sweep on {network}\n")
    text_log.insert(tk.END, f"[*] Total hosts to scan: {network.num_addresses - 2}\n")
    text_log.insert(tk.END, "-" * 55 + "\n")
    
    live_hosts = 0
    hosts_to_scan = [str(ip) for ip in network.hosts()]

    # Use ThreadPoolExecutor for highly concurrent network scanning
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_host, hosts_to_scan)
        
        for ip, is_up in results:
            if not is_sweeping:
                text_log.insert(tk.END, "\n[!] Sweep aborted by user.\n", "warning")
                break
                
            if is_up:
                live_hosts += 1
                text_log.insert(tk.END, f"[+] LIVE HOST: {ip} is UP\n", "success")
                text_log.see(tk.END)
                
            lbl_status.config(text=f"Scanning... Found {live_hosts} live hosts")

    if is_sweeping:
        text_log.insert(tk.END, "-" * 55 + "\n")
        text_log.insert(tk.END, f"[*] Sweep Complete. Total Live Hosts: {live_hosts}\n")
        
    text_log.see(tk.END)
    text_log.config(state=tk.DISABLED)
    reset_ui()

def start_sweep():
    global is_sweeping
    if is_sweeping: return
    
    is_sweeping = True
    btn_start.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)
    lbl_status.config(text="Initializing sweep...", fg="#e67e22")
    
    # Run the sweep on a background thread
    threading.Thread(target=run_sweep, daemon=True).start()

def stop_sweep():
    global is_sweeping
    is_sweeping = False

def reset_ui():
    global is_sweeping
    is_sweeping = False
    btn_start.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)
    lbl_status.config(text="READY", fg="#7f8c8d")

# --- Tkinter GUI Layout ---
root = tk.Tk()
root.title("NOC Toolkit - Subnet Ping Sweeper")
root.geometry("500x520")
root.resizable(False, False)

frame = ttk.Frame(root, padding="15")
frame.pack(fill=tk.BOTH, expand=True)

lbl_title = tk.Label(frame, text="Active Network Ping Sweeper", font=("Helvetica", 13, "bold"))
lbl_title.pack(anchor="w", pady=(0, 15))

# Target Configuration
config_frame = tk.Frame(frame)
config_frame.pack(fill=tk.X, pady=(0, 15))

tk.Label(config_frame, text="Target Subnet (CIDR):", font=("Helvetica", 9)).grid(row=0, column=0, sticky="w", pady=5)
entry_subnet = ttk.Entry(config_frame, width=20, font=("Consolas", 10))
entry_subnet.grid(row=0, column=1, padx=10, pady=5)
entry_subnet.insert(0, "192.168.1.0/24")

# Controls
control_frame = tk.Frame(frame)
control_frame.pack(fill=tk.X, pady=(0, 10))

btn_start = tk.Button(control_frame, text="Sweep Subnet", command=start_sweep, bg="#2980b9", fg="white", font=("Helvetica", 9, "bold"), width=15)
btn_start.pack(side=tk.LEFT, padx=(0, 10))

btn_stop = tk.Button(control_frame, text="Abort", command=stop_sweep, bg="#c0392b", fg="white", font=("Helvetica", 9, "bold"), width=10, state=tk.DISABLED)
btn_stop.pack(side=tk.LEFT)

lbl_status = tk.Label(control_frame, text="READY", font=("Helvetica", 9, "bold"), fg="#7f8c8d")
lbl_status.pack(side=tk.RIGHT, padx=(0, 5))

# Output Console
text_frame = tk.Frame(frame)
text_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_log = tk.Text(text_frame, font=("Consolas", 9), bg="#1e1e1e", fg="#ecf0f1", yscrollcommand=scrollbar.set)
text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
text_log.config(state=tk.DISABLED)

# Text Tag Configurations
text_log.tag_config("success", foreground="#2ecc71", font=("Consolas", 9, "bold"))
text_log.tag_config("warning", foreground="#f1c40f")

scrollbar.config(command=text_log.yview)

root.mainloop()