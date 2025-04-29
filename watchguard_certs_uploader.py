#!/usr/bin/env python3

import argparse
import random
import string
import multiprocessing
import os
import sys
from time import sleep

from netmiko.watchguard.fireware_ssh import WatchguardFirewareSSH
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def generate_password(length=16):
	characters = string.ascii_letters + string.digits
	return "".join(random.choice(characters) for _ in range(length))


def run_ftp_server(port, username, password):
	authorizer = DummyAuthorizer()
	authorizer.add_user(username, password, ".", perm="elr")

	handler = FTPHandler
	handler.authorizer = authorizer

	server = FTPServer(("0.0.0.0", port), handler)
	server.serve_forever()


def send_command(wgssh, cmd):

	response = wgssh.send_command_timing(cmd, read_timeout=5)
	sleep(0.1)


	return response


def main():
	parser = argparse.ArgumentParser(description="Send certificate(s) to WatchGuard firewall via FTP.")
	parser.add_argument("certs", nargs="+", help="Certificate file(s) to send (.pem or .pfx)")
	parser.add_argument("--ftp-host", required=True, help="FTP server host, your IP (e.g., 192.168.1.80)")
	parser.add_argument("--ftp-port", type=int, default=2121, help="FTP server port (default: 2121)")
	parser.add_argument("--wg-host", required=True, help="WatchGuard host (e.g., 192.168.1.243)")
	parser.add_argument("--wg-port", type=int, default=4118, help="WatchGuard port (default: 4118)")
	parser.add_argument("--wg-username", required=True, help="WatchGuard username")
	parser.add_argument("--wg-password", required=True, help="WatchGuard password")
	parser.add_argument("--pfx-password", default=None, help="Password for PFX file, if needed")

	args = parser.parse_args()

	# FTP user and password
	ftp_username = generate_password()
	ftp_password = generate_password()

	# Start FTP server
	ftp_process = multiprocessing.Process(target=run_ftp_server, args=(args.ftp_port, ftp_username, ftp_password))
	ftp_process.start()

	# Connect to WatchGuard
	try:
		wgssh = WatchguardFirewareSSH(
			ip=args.wg_host, host=args.wg_host, username=args.wg_username, password=args.wg_password, port=args.wg_port
		)
	except Exception as e:
		if e.args[0] == "Socket is closed":
			print("Error connecting to WatchGuard, try disconnect yourself")
		else:
			print(f"Error connecting to WatchGuard: {e}")
		ftp_process.terminate()
		sys.exit(1)

	sleep(2)

	# Upload certs
	for cert in args.certs:
		filename = os.path.basename(cert)
		if not os.path.exists(cert):
			print(f"Certificate {cert} does not exist.")
			continue


		# Build the command
		if filename.lower().endswith(".pfx"):
			if args.pfx_password:
				cmd = f"import certificate general-usage from ftp://{args.ftp_host}:{args.ftp_port}/{cert} {args.pfx_password}"
			else:
				print(f"Skipping PFX {filename} because no --pfx-password provided.")
				continue
		else:
			cmd = f"import certificate general-usage from ftp://{args.ftp_host}:{args.ftp_port}/{cert}"

		# Execute the import
		print(f"Sending: {cmd}")
		send_command(wgssh, cmd)
		send_command(wgssh, ftp_username)
		response = send_command(wgssh, ftp_password)
		if "Error" in response:
			print(response)
			result_str = ""
		else:
			result_str = "Certificates uploaded and "


	# Exit
	wgssh.send_command_timing("exit", read_timeout=3)
	wgssh.disconnect()
	wgssh.paramiko_cleanup()

	ftp_process.terminate()
	ftp_process.join()

	print(f"{result_str}WatchGuard session closed successfully.")


if __name__ == "__main__":
	main()


