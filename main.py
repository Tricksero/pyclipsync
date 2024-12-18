from configparser import ConfigParser
import pyperclip
import paramiko
import logging
import time


CONFIG_NAME = "config.ini"
config = ConfigParser()
config.read(CONFIG_NAME)

# Replace these with your remote machine details in the config
remote_host = config.get("ssh", "hostname", fallback="127.0.0.1")
remote_port = config.getint("ssh", "port", fallback=22)
remote_username = config.get("ssh", "username", fallback="test")
# get_command = 'xclip -o -selection clipboard' # xclip retrieves clipboard
# set_command = "echo '{}' | xclip -selection clipboard" # xclip sets clipboard
get_command = "cat -e ~/.local/share/nvim/clipboard_history.txt"
# AcceptEnv CLIP must be set in sshd_config on host
set_command = 'echo $CLIP > ~/.local/share/nvim/clipboard_history.txt'
print(remote_host, remote_port, remote_username)

def send_command(host, port, username, command, environment) -> str | None:
    # Initialize SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_log_channel(None)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote machine
        response = ssh_client.connect(host, port=port, username=username)
        
        # Execute the command on the remote machine
        # logging.info("command", command)
        stdin, stdout, stderr = ssh_client.exec_command(command, environment=environment)
        # logging.info("message", stdout)
        
        # Read the output from the command
        clipboard_content = stdout.read().decode()
        return clipboard_content
    
    except Exception as e:
        print(f"Error accessing remote clipboard: {e}")
        return None
    
    finally:
        # Close the SSH connection
        ssh_client.close()

from logging import Logger, FileHandler, Formatter
logger = Logger("clipboard_logger", level=logging.DEBUG)
# formatter = Formatter()
handler = FileHandler(filename='ssh_connection.log', mode="a")
logger.addHandler(handler)

#format='%(asctime)s - %(message)s'
#logging.basicConfig()
                    

clipboard_content_old = pyperclip.paste().replace("\r\n", "\n")

while True:
    # Get the current clipboard content
    clipboard_content_local = pyperclip.paste().replace("\r\n", "\n")
    clipboard_content_remote = send_command(remote_host, remote_port, remote_username, get_command, None)
    # Check if it has changed
    if repr(clipboard_content_remote) != repr(clipboard_content_old):
        logger.debug(f"1 Clipboard remote: {clipboard_content_remote}")
        logger.debug(f"1 Clipboard local: {repr(clipboard_content_local)}")
        logger.debug(f"1 Clipboard old: {repr(clipboard_content_old)}")
        pyperclip.copy(clipboard_content_remote)
        clipboard_content_old = clipboard_content_remote

    if repr(clipboard_content_local) != repr(clipboard_content_old):
        logger.debug(f"2 Clipboard local: {repr(clipboard_content_local)}")
        logger.debug(f"2 Clipboard remote: {clipboard_content_remote}")
        logger.debug(f"2 Clipboard old: {repr(clipboard_content_old)}")
        #send_command(remote_host, remote_port, remote_username, set_command, environment={"CLIP": clipboard_content_local})
        clipboard_content_old = clipboard_content_local

    time.sleep(0.5)