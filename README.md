<h1 align="center">Comic-fuz Manga Downloader GUI</h1>
<p align="center"><img src="https://i.imgur.com/LhjPTdo.png" width=200 height=200></p>
<p align="center"><i>Download manga you rent from <a href="https://comic-fuz.com/">https://comic-fuz.com/</a>.</i></p>

English | [中文文档](docs/README_zh-CN.md)

<br>

# Download

Go to the [release page](https://github.com/ipid/ComicFuz-Downloader-GUI/releases) for packed binaries. Currently only Windows executable is provided.

<br>

# Prerequisite

You need to install a browser extension to export the `cookies.txt`. 

We recommend [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid) for Chrome users; however, extensions for Firefox have not been tested yet.

<br>

# Usage

<p align="center"><img src="https://i.imgur.com/Buo5msj.png"></p>

1. Export cookies.txt with the browser extension.
2. Specify all the information, then click **Fetch**.
3. After manga info were fetched, click **Download**.

You may not want to download the whole magazine/manga, but a part of it. You can specify the page range in the Download Options with the following syntax. For example:

- Download page 12: `12`
- Download page 1, page 2 to 10 (includes page 10), and page 12: `1, 2-10, 12`
- Download page 10 to 20 and page 50 to 60: `10-20, 50-60`

<br>

# Dev: Run the script directly

The project is merely some Python codes, so you can run the code with plain Python.
You will need Python 3.9 or above.

- First of all, run `pip install -r requirements.txt` to install all the required packages.
  - We suggest you use `venv` because there are some useless requirements if you only want to run the script.
- Then, run `main.py`.

<br>

# Dev: Create your own executable

The official released executable is packed with **PyInstaller**. We use these parameters to pack the scripts:

```shell
pyinstaller --clean --onefile --windowed --icon assets/logo-icon.ico --name ComicFuz-Downloader-GUI --hidden-import urllib3.contrib.socks main.py
```

To pack the project, you need to install PyInstaller and all the requirements of the project. These requirements, including PyInstaller, are defined in the `requirements.txt`. Thus, we suggest you install the PyInstaller  with `pip install -r requirements.txt` and under `venv`, then pack the executable with the command listed above.
