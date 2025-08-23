import argparse
import socket
import struct
import sys
import time

import cv2
import numpy as np


def recv_exact(sock: socket.socket, num_bytes: int) -> bytes:
	data = bytearray()
	while len(data) < num_bytes:
		chunk = sock.recv(num_bytes - len(data))
		if not chunk:
			raise ConnectionError("Socket closed while receiving data")
		data.extend(chunk)
	return bytes(data)


def connect_once(host: str, port: int, window_title: str) -> None:
	with socket.create_connection((host, port), timeout=5.0) as sock:
		sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		print(f"Connected to {host}:{port}")
		while True:
			# Read 4-byte big-endian length
			length_be = recv_exact(sock, 4)
			(frame_len,) = struct.unpack("!i", length_be)
			if frame_len <= 0 or frame_len > 50_000_000:
				raise ValueError(f"Invalid frame length: {frame_len}")

			# Read JPEG payload
			jpg_bytes = recv_exact(sock, frame_len)
			np_buf = np.frombuffer(jpg_bytes, dtype=np.uint8)
			img = cv2.imdecode(np_buf, cv2.IMREAD_COLOR)
			if img is None:
				print("Warning: failed to decode frame", file=sys.stderr)
				continue

			cv2.imshow(window_title, img)
			# 1 ms wait allows window events; ESC to quit
			key = cv2.waitKey(1) & 0xFF
			if key == 27:
				break

	cv2.destroyAllWindows()


def main() -> None:
	parser = argparse.ArgumentParser(description="Receive and display Unity camera stream over TCP")
	parser.add_argument("--host", default="127.0.0.1", help="Server host/IP (default: 127.0.0.1)")
	parser.add_argument("--port", type=int, default=5001, help="Server port (default: 5001)")
	parser.add_argument("--retry", type=int, default=3, help="Reconnect attempts (-1 infinite)")
	parser.add_argument("--delay", type=float, default=1.0, help="Delay between retries in seconds")
	args = parser.parse_args()

	retries_remaining = args.retry
	while True:
		try:
			connect_once(args.host, args.port, window_title=f"Unity Stream {args.host}:{args.port}")
			break
		except (ConnectionError, OSError, ValueError) as exc:
			print(f"Connection error: {exc}")
			if retries_remaining == 0:
				print("No more retries. Exiting.")
				break
			if retries_remaining > 0:
				retries_remaining -= 1
			print(f"Retrying in {args.delay:.1f}s... ({'infinite' if args.retry < 0 else retries_remaining} left)")
			time.sleep(args.delay)


if __name__ == "__main__":
	main()


