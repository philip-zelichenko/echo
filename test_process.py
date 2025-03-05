import psutil

def print_echo_processes():
    """Print all Echo Assistant related processes"""
    print("\nScanning processes...")
    
    # Group processes by type
    resource_trackers = []
    app_processes = []
    cli_processes = []
    other_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            cmdline = ' '.join(proc.cmdline()).lower() if proc.cmdline() else ''
            if "echo" in cmdline:
                if "resource_tracker" in cmdline:
                    resource_trackers.append((proc.pid, proc.status(), cmdline))
                elif "echo assistant.app" in cmdline:
                    app_processes.append((proc.pid, proc.status(), cmdline))
                elif "echo.cli" in cmdline:
                    cli_processes.append((proc.pid, proc.status(), cmdline))
                else:
                    other_processes.append((proc.pid, proc.status(), cmdline))
        except:
            continue
    
    # Print grouped processes
    if resource_trackers:
        print("\nResource Tracker Processes:")
        for pid, status, cmdline in resource_trackers:
            print(f"PID {pid} ({status}): {cmdline}")
    
    if app_processes:
        print("\nApp Bundle Processes:")
        for pid, status, cmdline in app_processes:
            print(f"PID {pid} ({status}): {cmdline}")
    
    if cli_processes:
        print("\nCLI Processes:")
        for pid, status, cmdline in cli_processes:
            print(f"PID {pid} ({status}): {cmdline}")
    
    if other_processes:
        print("\nOther Echo Processes:")
        for pid, status, cmdline in other_processes:
            print(f"PID {pid} ({status}): {cmdline}")

if __name__ == "__main__":
    print_echo_processes()