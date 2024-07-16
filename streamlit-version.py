import psutil
import streamlit as st
import pandas as pd
import time

# Function to display memory information
def display_memory_info():
    memory_info = psutil.virtual_memory()
    st.subheader("Memory Information")
    st.metric(label="Total Memory", value=f"{memory_info.total / (1024 ** 3):.2f} GB")
    st.metric(label="Available Memory", value=f"{memory_info.available / (1024 ** 3):.2f} GB")
    st.metric(label="Used Memory", value=f"{memory_info.used / (1024 ** 3):.2f} GB")
    st.metric(label="Memory Usage Percentage", value=f"{memory_info.percent:.2f}%")

# Function to display running processes
def display_processes():
    processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'memory_info']):
        processes.append([proc.info['pid'], proc.info['name'], proc.info['memory_info'].rss / (1024 ** 2)])
    processes_df = pd.DataFrame(processes, columns=['PID', 'Name', 'Memory (MB)'])
    processes_df.sort_values(by='Memory (MB)', ascending=False, inplace=True)
    st.subheader("Running Processes (sorted by memory usage)")
    st.dataframe(processes_df)

# Function to monitor memory usage of a specific application
def monitor_memory_usage(application_name):
    try:
        while True:
            memory_info = psutil.virtual_memory()
            processes = [proc for proc in psutil.process_iter(attrs=['pid', 'name', 'memory_info']) if application_name in proc.info['name']]
            if processes:
                total_memory = sum(proc.info['memory_info'].rss for proc in processes)
                application_memory = total_memory
                total_system_memory = memory_info.total
                memory_percentage = (application_memory / total_system_memory) * 100
                st.subheader(f"Monitoring Memory Usage of '{application_name}'")
                st.metric(label="Total System Memory", value=f"{total_system_memory / (1024 ** 3):.2f} GB")
                st.metric(label=f"{application_name} Memory Usage", value=f"{application_memory / (1024 ** 3):.2f} GB")
                st.metric(label=f"Memory Usage Percentage by {application_name}", value=f"{memory_percentage:.2f}%")
            else:
                st.warning(f"No process found with name '{application_name}'")
            
            time.sleep(1)  # Update every 1 second
    except KeyboardInterrupt:
        pass

# Function to stop a specific application
def stop_application(application_name):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if application_name.lower() in proc.info['name'].lower():
            try:
                process = psutil.Process(proc.info['pid'])
                process.terminate()
                st.success(f"Process '{application_name}' (PID: {proc.info['pid']}) has been terminated.")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                st.error(f"Failed to terminate process '{application_name}'")

# Function to get user applications
def get_user_applications():
    user_applications = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'memory_info', 'username']):
        if proc.info['username'] and proc.info['username'] != 'SYSTEM':
            user_applications.append(proc)
    return user_applications

# Function to terminate highest memory consuming application
def terminate_highest_memory_application():
    try:
        user_applications = get_user_applications()
        highest_memory_process = max(user_applications, key=lambda proc: proc.info['memory_info'].rss, default=None)
        
        if highest_memory_process:
            st.subheader("Terminating Highest Memory Consuming User Application")
            st.write(f"**Application Name:** {highest_memory_process.info['name']}")
            st.write(f"**Memory Usage:** {highest_memory_process.info['memory_info'].rss / (1024 ** 2):.2f} MB")
            if st.button("Terminate"):
                try:
                    process = psutil.Process(highest_memory_process.info['pid'])
                    process.terminate()
                    st.success(f"Process '{highest_memory_process.info['name']}' (PID: {highest_memory_process.info['pid']}) has been terminated.")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    st.error(f"Failed to terminate process '{highest_memory_process.info['name']}'")
        else:
            st.warning("No running user applications found.")
    except KeyboardInterrupt:
        pass

# Main function to run the Streamlit app
def main():
    st.title("Memory Management Dashboard")
    st.sidebar.title("Menu")
    menu_options = ["Display Memory Information", "Display Running Processes", "Monitor Memory Usage of a Specific Application",
                    "Stop a Specific Application", "Terminate Highest Memory Consuming Application"]
    choice = st.sidebar.radio("Select an option", menu_options)

    if choice == "Display Memory Information":
        display_memory_info()
    elif choice == "Display Running Processes":
        display_processes()
    elif choice == "Monitor Memory Usage of a Specific Application":
        processes = [proc.info for proc in psutil.process_iter(attrs=['name'])]
        application_names = [proc['name'] for proc in processes]
        selected_app = st.selectbox("Select the application to monitor", application_names)
        if st.button("Monitor"):
            monitor_memory_usage(selected_app)
    elif choice == "Stop a Specific Application":
        processes = [proc.info for proc in psutil.process_iter(attrs=['name'])]
        application_names = [proc['name'] for proc in processes]
        selected_app = st.selectbox("Select the application to stop", application_names)
        if st.button("Stop"):
            stop_application(selected_app)
    elif choice == "Terminate Highest Memory Consuming Application":
        if st.button("Terminate"):
            terminate_highest_memory_application()

if __name__ == "__main__":
    main()
