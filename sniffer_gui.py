import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scapy.all import sniff
from scapy.layers.inet import IP
from datetime import datetime
import threading

running = False
captured_logs = []

# ---------- packet handler ----------
def packet_handler(packet):
    global running

    if not running:
        return False

    if IP in packet:
        src = packet[IP].src
        dst = packet[IP].dst
        proto = packet[IP].proto
        size = len(packet)
        time_now = datetime.now().strftime("%H:%M:%S")

        if proto == 6:
            proto_name = "TCP"
        elif proto == 17:
            proto_name = "UDP"
        elif proto == 1:
            proto_name = "ICMP"
        else:
            proto_name = str(proto)

        row = (time_now, proto_name, src, dst, size)

        tree.insert("", tk.END, values=row)
        tree.yview_moveto(1)

        log_line = f"{time_now} | {proto_name} | {src} -> {dst} | {size} bytes"
        captured_logs.append(log_line)


# ---------- sniff thread ----------
def sniff_packets():
    sniff(prn=packet_handler, store=False)


# ---------- buttons ----------
def start_sniffing():
    global running

    if not running:
        running = True
        status_label.config(text="Status: Running")
        thread = threading.Thread(target=sniff_packets, daemon=True)
        thread.start()


def stop_sniffing():
    global running
    running = False
    status_label.config(text="Status: Stopped")


def export_logs():
    if not captured_logs:
        messagebox.showinfo("Info", "No logs to export")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt")

    if file_path:
        with open(file_path, "w") as f:
            for log in captured_logs:
                f.write(log + "\n")

        messagebox.showinfo("Saved", "Logs exported successfully")


# ---------- GUI ----------
root = tk.Tk()
root.title("Basic Network Sniffer")
root.geometry("950x500")

frame = tk.Frame(root)
frame.pack(pady=10)

start_btn = tk.Button(frame, text="Start", width=15, command=start_sniffing)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(frame, text="Stop", width=15, command=stop_sniffing)
stop_btn.grid(row=0, column=1, padx=10)

export_btn = tk.Button(frame, text="Export Log", width=15, command=export_logs)
export_btn.grid(row=0, column=2, padx=10)

status_label = tk.Label(root, text="Status: Stopped", font=("Arial", 12))
status_label.pack()

columns = ("Time", "Protocol", "Source IP", "Destination IP", "Size")

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=170)

tree.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()
