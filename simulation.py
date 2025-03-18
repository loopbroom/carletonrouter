import time
import random
import fcntl

file_path = 'StatefulHardware.txt'

def calculate_f(a, b, c, d, p, q, m, n):
    return p**a * q**b * m**c * n**d

def read_hardware_state(file_path):
    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        lines = file.readlines()
        if len(lines) < 3:
            fcntl.flock(file, fcntl.LOCK_UN)
            file.close()
            return read_hardware_state(file_path)
        state_line = lines[0].strip()
        control_line = lines[1].strip()
        signal_line = lines[2].strip()
        state_values = [int(value) for value in state_line.split(',')]
        control_values = [int(value) for value in control_line.split(',')]
        signal_values = [int(value) for value in signal_line.split(',')]
        fcntl.flock(file, fcntl.LOCK_UN)
        file.close()
        return state_values, control_values, signal_values

def write_hardware_state(file_path, state_values, control_values, signal_values):
    with open(file_path, 'w') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        state_line = ','.join(str(value) for value in state_values)
        control_line = ','.join(str(value) for value in control_values)
        signal_line = ','.join(str(value) for value in signal_values)
        file.write(state_line + '\n')
        file.write(control_line + '\n')
        file.write(signal_line + '\n')
        fcntl.flock(file, fcntl.LOCK_UN)
        file.close()

def mutate_hardware(file_path, index, value):
    state_values, control_values, signal_values = read_hardware_state(file_path)
    control_values[index] = value
    write_hardware_state(file_path, state_values, control_values, signal_values)

def mutate_database(file_path, index, value):
    state_values, control_values, signal_values = read_hardware_state(file_path)
    state_values[index] = value
    write_hardware_state(file_path, state_values, control_values, signal_values)

def mutate_signal(file_path, index, value):
    state_values, control_values, signal_values = read_hardware_state(file_path)
    signal_values[0] = index
    signal_values[1] = value
    write_hardware_state(file_path, state_values, control_values, signal_values)

def create_hardware_file(file_path):
    initial_state_values = [1, 2, 3, 4]
    initial_control_values = [5, 6, 7, 8]
    initial_signal_values = [0, 0]
    write_hardware_state(file_path, initial_state_values, initial_control_values, initial_signal_values)

def main():
    # Create the hardware file if it doesn't exist
    try:
        with open(file_path, 'r'):
            pass
    except FileNotFoundError:
        create_hardware_file(file_path)
    t = 0
    while True:
        t += 1
        state_values, control_values, signal_values = read_hardware_state(file_path)
        result = calculate_f(*state_values, *control_values)
        print(f"state_values = {state_values}, control_values = {control_values}, signal_values = {signal_values}, f(txt file) = {result}")

        # Example mutation
        if t % 6 == 0:
            random_index = random.randint(1, 4)  # Generate a random index
            random_value = random.randint(1, 8)  # Generate a random value
            mutate_signal(file_path, random_index, random_value)

        time.sleep(1)  # Wait for 1 second before polling again

if __name__ == '__main__':
    main()