import sys
import time
import select

from simulation import read_hardware_state, write_hardware_state, mutate_hardware, mutate_database, create_hardware_file, file_path

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
                print(f"Invalid Input - Error: {index + 1} is an invalid index")
            else:
                mutate_database(file_path, index, value)
                history.append(f"{t} set {index} {value}")
    except Exception as e:
        print(f"Invalid Input - Error: {str(e)}")

def main():
    history = []
    t = 0

    # Keep track of the last seen signal values
    last_signal_index = 0
    last_signal_value = 0

    create_hardware_file("StatefulHardware.txt")

    print("Enter CLI command: ")

    try:
        while t < 60:
            current_state, control_values, signal_values = read_hardware_state(file_path)
            t += 1

            # Case 2: Handling Control Traffic
            # Process signals from the signal_values
            signal_index = signal_values[0]
            signal_value = signal_values[1]
            
            # If signal_index is 1-4, update the corresponding control value
            if (signal_index != last_signal_index or signal_value != last_signal_value) and 1 <= signal_index <= 4:
                mutate_hardware(file_path, signal_index - 1, signal_value)
                history.append(f"{t} set {signal_index - 1} {signal_value}")
                
                # Update the last seen values
                last_signal_index = signal_index
                last_signal_value = signal_value

            # Case 3: Allow CLI input for manual configuration
            # Check if there's any input available without blocking
            i, _, _ = select.select([sys.stdin], [], [], 0)
            if i:
                process_cli_input(file_path, history, t)
            
            # Case 4: Cron Job - swap state values at indices 1 and 2 when t is multiple of 10
            if t % 10 == 0:
                # Swap the values at indices 0 and 1 (0-indexed, which is 1 and 2 in 1-indexed)
                temp = current_state[0]
                current_state[0] = current_state[1]
                current_state[1] = temp
                
                # Write the updated state back
                write_hardware_state(file_path, current_state, control_values, signal_values)
                
                # Record the swap in history
                history.append(f"{t} swap {current_state[1]} {current_state[0]}")
            

            time.sleep(1)  # Wait for 1 second before polling again
    
    # Case 5: Recovery and Documentation - write router log on program termination

    finally:
        # Write history to log file upon program termination
        print(history)
        with open('router_history.log', 'w') as log_file:
            for entry in history:
                log_file.write(entry + '\n')
        
        print("History has been written to router_history.log")

if __name__ == '__main__':
    main()
