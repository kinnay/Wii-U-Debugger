# Wii-U-Debugger
This is a rewrite of [DiiBugger](https://github.com/Kinnay/DiiBugger) for the homebrew launcher.

In addition to homebrew launcher compatibility, it has received various improvements, most notably:
* Better breakpoint support. The old debugger assumed only one thread was active at once. It wouldn't work correctly or crash when two threads hit a breakpoint at the same time. The new implementation allows multiple threads to be paused at the same time and lets you step through them independently.
* A tab that displays the loaded modules
* A bunch of bug fixes and improved reliability

However, it still isn't possible to launch certain system apps under this debugger (such as the internet browser). If you try to do so, it will crash.

To set a breakpoint, click on an instruction in the disassembly with the scroll wheel / middle mouse button.

# Screenshots
<div style="float: left">
  <img src="https://www.dropbox.com/s/a8dzm644hqc3clg/memory.png?raw=1" width="250"/>
  <img src="https://www.dropbox.com/s/2m9wst0fbl59by0/disassembly.png?raw=1" width="250"/>
  <img src="https://www.dropbox.com/s/xdoxzf8kafnm3al/threads.png?raw=1" width="250"/><br>
  <img src="https://www.dropbox.com/s/jahakofophuv02j/modules.png?raw=1" width="250"/>
  <img src="https://www.dropbox.com/s/shmpz7u58oxby75/exceptions.png?raw=1" width="250"/>
</div>
