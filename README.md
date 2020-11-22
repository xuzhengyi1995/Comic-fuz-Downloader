<h1 align="center">Comic-fuz Manga Downloader GUI</h1>
<p align="center"><img src="https://i.imgur.com/LhjPTdo.png" width=200 height=200></p>
<p align="center"><i>Download manga you rent from <a href="https://comic-fuz.com/">https://comic-fuz.com/</a>.</i></p>

English | [中文文档](docs/README_zh-CN.md)

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
