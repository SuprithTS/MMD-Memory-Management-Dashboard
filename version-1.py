import os
import time
import psutil

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_dashboard():
    clear_screen()
    print("Memory Management Dashboard\n")
    print("1. Display Memory Information")
    print("2. Monitor Memory Usage of a Specific Application")
    print("3. Stop a Specific Application")
    print("4. Exit")
    choice = input("\nEnter your choice: ")
    return choice

def display_memory_info():
    memory_info = psutil.virtual_memory()
    print("\nMemory Information:")
    print(f"Total Memory: {memory_info.total} bytes")
    print(f"Available Memory: {memory_info.available} bytes")
    print(f"Used Memory: {memory_info.used} bytes")
    print(f"Memory Usage Percentage: {memory_info.percent:.2f}%")
    input("\nPress Enter to continue...")

def monitor_memory_usage(application_name):
    try:
        while True:
            memory_info = psutil.virtual_memory()
            clear_screen()
            print(f"Monitoring Memory Usage of '{application_name}' (Press Ctrl+C to stop)...\n")
            processes = [proc for proc in psutil.process_iter(attrs=['pid', 'name', 'memory_info']) if application_name in proc.info['name']]
            if processes:
                total_memory = sum(proc.info['memory_info'].rss for proc in processes)
                application_memory = total_memory
                total_system_memory = memory_info.total
                memory_percentage = (application_memory / total_system_memory) * 100
                print(f"Total System Memory: {total_system_memory} bytes")
                print(f"\n'{application_name}' Memory Usage: {application_memory} bytes")
                print(f"Memory Usage Percentage by '{application_name}' : {memory_percentage:.2f}%")
            else:
                print(f"No process found with name '{application_name}'")
            time.sleep(1.5)  # Update every 2 seconds
    except KeyboardInterrupt:
        pass


def stop_application(application_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if application_name.lower() in proc.info['name'].lower():
            try:
                process = psutil.Process(proc.info['pid'])
                process.terminate()
                print(f"Process '{application_name}' (PID: {proc.info['pid']}) has been terminated.")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Handle cases where the process is not found or termination is denied

def main():
    while True:
        choice = display_dashboard()

        if choice == "1":
            display_memory_info()
        elif choice == "2":
            all_process_names = [proc.info['name'] for proc in psutil.process_iter(attrs=['name'])]
            print("All running process names:", all_process_names)

            application_name = input("\nEnter the name of the application to monitor: ")
            monitor_memory_usage(application_name)
        elif choice == "3":
            application_name = input("Enter the name of the application to stop: ")
            stop_application(application_name)
        elif choice == "4":
            print("Exiting the Memory Management Dashboard...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
