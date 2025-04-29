# WatchGuard Certificate Uploader

A Python utility for automated certificate imports to WatchGuard Firebox devices through a temporary FTP service.

## Features

- Automated certificate imports to WatchGuard Firebox devices
- Temporary secure FTP server with auto-generated credentials
- Support for both PEM and PFX certificate formats
- Multi-certificate upload in a single operation
- Command-line interface with comprehensive options

## Requirements

- Tested on python 3.12
- Required Python packages:
  - netmiko
  - pyftpdlib

## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/1SWISS1/watchguard_certs_uploader.git
   cd watchguard_certs_uploader
   ```

2. Install the dependencies
   ```bash
   pip install netmiko pyftpdlib
   ```

3. Make the script executable
   ```bash
   chmod +x watchguard_certs_uploader.py
   ```

## Compiled Version

A compiled version is available for Debian 11+ systems in the release page. You can compile it yourself using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --hidden-import netmiko --hidden-import pyftpdlib watchguard_certs_uploader.py
```

## Usage

```bash
./watchguard_certs_uploader.py [certificate files] --ftp-host [your-ip] --wg-host [watchguard-ip] --wg-username [username] --wg-password [password] [options]
```

### Required Arguments

- `certificate files`: One or more certificate files (.pem or .pfx)
- `--ftp-host`: Your local IP address where the FTP server will run
- `--wg-host`: IP address of the WatchGuard device
- `--wg-username`: WatchGuard admin username
- `--wg-password`: WatchGuard admin password

### Optional Arguments

- `--ftp-port`: Port for the FTP server (default: 2121)
- `--wg-port`: WatchGuard SSH port (default: 4118)
- `--pfx-password`: Password for PFX certificate files (required for PFX imports)

## Examples

### Uploading a PEM certificate:

```bash
./watchguard_certs_uploader.py certs/wildcard_example.com.pem \
--ftp-host 192.168.1.80 --wg-host 192.168.1.243 \
--wg-username admin --wg-password yourpassword
```

### Uploading multiple certificates including a PFX file:

```bash
./watchguard_certs_uploader.py root_certs/ca.pem certs/wildcard_example.com.pfx \
--ftp-host 192.168.1.80 --wg-host 192.168.1.243 \
--wg-username admin --wg-password yourpassword --pfx-password pfxpassword
```

## How It Works

1. The script starts a temporary FTP server on your machine with randomly generated credentials
2. It establishes an SSH connection to the WatchGuard device
3. It issues commands to the WatchGuard to import certificates from your FTP server
4. The FTP server is automatically terminated when the operation completes

## Security Notes

- The tool generates random credentials for the FTP server with each execution
- FTP credentials are only used for the duration of the certificate transfer
- Ensure you're using this tool in a secure network environment
- Consider using a dedicated management network for WatchGuard administration

## License

[MIT License](LICENSE)

