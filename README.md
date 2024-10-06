# Pyclipsync
Uses python to synchronize clipboards over ssh.

There are a lot of programs that have this feature like Barrier or Desktop
sharing Programs in general. I wanted a program that does this and nothing else.

## Requirements
### Python
```sh
pip install uv
uv pip compile ./requirements.in > requirements.txt
uv pip sync ./requirements.txt
```
### Target Machine
- Running X-Server
- xclip installed

## Usage
I ran this on windows connecting to linux.
Any other configuration between windows or linux systems *should work:tm:*.

### Linux
As you probably know the clipboard on Linux is usually managed by the windowing system, as I tend to use the
X windowing system over wayland there is currently no wayland support.

## License
This Project uses a [MIT License](./LICENSE)