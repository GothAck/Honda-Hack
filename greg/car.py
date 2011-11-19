
import socket
from select import select


UDP_IP="127.0.0.1"
UDP_PORT=5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
last_known_state = {
    "speed": 10,
    "gear": 0,
    "rpm": 60,
}
prev_known_state = {}


def get_car_state():
    try:
        while True:
            [r, w, x] = select([sock, ], [], [], 0)
            if r:
                data, addr = sock.recvfrom(1024)
                last_known_state.update(dict([e.split("=") for e in data.split(",")]))
            else:
                break
    except Exception as e:
        print "Fail at getting state", e
    return last_known_state


def get_car_change():
    old_state = prev_known_state.copy()
    new_state = get_car_state()
    diff_state = {}
    for key in old_state:
        if old_state[key] != new_state[key]:
            diff_state[key] = new_state[key]
    prev_known_state.update(new_state)
    return (old_state, new_state, diff_state)
