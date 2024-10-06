from configparser import ConfigParser
import pyperclip
import paramiko
import logging
import time

logger = logging.basicConfig(filename='ssh_connection.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

CONFIG_NAME = "config.ini"
config = ConfigParser()
config.read(CONFIG_NAME)

# Replace these with your remote machine details in the config
remote_host = config.get("ssh", "hostname", fallback="127.0.0.1")
remote_port = config.getint("ssh", "port", fallback=22)
remote_username = config.get("ssh", "username", fallback="test")
get_command = 'xclip -o -selection clipboard' # xclip retrieves clipboard
set_command = "echo '{}' | xclip -selection clipboard" # xclip sets clipboard

def send_command(host, port, username, command) -> str | None:
    # Initialize SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote machine
        ssh_client.connect(host, port=port, username=username)
        
        # Execute the command on the remote machine
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Read the output from the command
        clipboard_content = stdout.read().decode().strip()
        return clipboard_content
    
    except Exception as e:
        print(f"Error accessing remote clipboard: {e}")
        return None
    
    finally:
        # Close the SSH connection
        ssh_client.close()

clipboard_content_old = ""
while True:
    # Get the current clipboard content
    clipboard_content_local = pyperclip.paste()
    clipboard_content_remote = send_command(remote_host, remote_port, remote_username, get_command)
    if clipboard_content_remote:
        logger.info(f"Clipboard content on remote machine: {clipboard_content_remote}")
    else:
        logger.info("Failed to retrieve clipboard content.")
        time.sleep(2)
        continue
        
    # Check if it has changed
    if clipboard_content_remote != clipboard_content_old:
        logger.info(f"Clipboard local: {clipboard_content_remote}")
        logger.info(f"Clipboard remote: {clipboard_content_local}")
        pyperclip.copy(clipboard_content_remote)
        clipboard_content_old = clipboard_content_remote

    if clipboard_content_local != clipboard_content_old:
        logger.info(f"Clipboard local: {clipboard_content_remote}")
        logger.info(f"Clipboard remote: {clipboard_content_local}")
        send_command(remote_host, remote_port, remote_username, set_command.format(clipboard_content_local))
        clipboard_content_old = clipboard_content_local

    time.sleep(0.5)