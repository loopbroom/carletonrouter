import subprocess
import sys
import time
import select

from simulation import read_hardware_state, write_hardware_state, calculate_f, mutate_hardware, mutate_database, create_hardware_file, file_path

def print_cli_history(history):
    for entry in history:
        print(entry)

def process_cli_input(file_path, history, t):
    # Process CLI input here
    try:
        user_input = input("Enter CLI command: ")
        command, *args = user_input.split()
        if command == "set":
            index = int(args[0]) - 1
            value = int(args[1])
            if index < 0 or index >3 :
                print(f"Invalid Input - Error: {index}")
            else:
                mutate_database(file_path, index, value)
                history.append(f"{t} set {index} {value}")
    except Exception as e:
        print(f"Invalid Input - Error: {str(e)}")

def main():
    history = []
    t = 0

    try:
        while t < 60:
            state_values, control_values, signal_values = read_hardware_state(file_path)
            t += 1

            # Write Your Code Here Start
            
            # Case 2 & 3: Handling Control Traffic and Management Functionality
            # Process signals from the signal_values
            signal_index = signal_values[0]
            signal_value = signal_values[1]
            
            # If signal_index is 1-4, update the corresponding control value
            if 1 <= signal_index <= 4:
                mutate_hardware(file_path, signal_index - 1, signal_value)
                history.append(f"{t} set {signal_index - 1} {signal_value}")
            
            # Case 4: Cron Job - swap state values at indices 1 and 2 when t is multiple of 10
            if t % 10 == 0:
                # Get the current state values
                current_state, _, _ = read_hardware_state(file_path)
                
                # Swap the values at indices 0 and 1 (0-indexed, which is 1 and 2 in 1-indexed)
                temp = current_state[0]
                current_state[0] = current_state[1]
                current_state[1] = temp
                
                # Write the updated state back
                write_hardware_state(file_path, current_state, control_values, signal_values)
                
                # Record the swap in history
                history.append(f"{t} swap {current_state[1]} {current_state[0]}")
            
            # Case 5: Allow CLI input for manual configuration
            # Check if there's any input available without blocking
            i, o, e = select.select([sys.stdin], [], [], 0)
            if i:
                process_cli_input(file_path, history, t)

            # Write Your Code Here End

            time.sleep(1)  # Wait for 1 second before polling again
    
    finally:
        # Write history to log file upon program termination
        with open('router_history.log', 'w') as log_file:
            for entry in history:
                log_file.write(entry + '\n')
        
        print("History has been written to router_history.log")

if __name__ == '__main__':
    main()
