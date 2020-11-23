<h1 align="center">Comic FUZ 漫画下载器 GUI</h1>
<p align="center"><img src="https://i.imgur.com/LhjPTdo.png" width=150 height=150></p>
<p align="center"><i>下载您在 <a href="https://comic-fuz.com/">https://comic-fuz.com/</a> 上租赁的漫画。</i></p>

[English](../README.md) | 中文文档

<br>

# 下载

请前往 [Release 页面](https://github.com/ipid/ComicFuz-Downloader-GUI/releases) 下载最新版的软件。目前只提供 Windows 版的可执行文件。

<br>

# 使用前准备

您需要安装一个浏览器插件，来导出 `cookies.txt`。只有登录了 Comic FUZ 的用户才能下载漫画，因此本下载器需要您提供您的 cookies。

对于 Chrome 用户，我们推荐您使用 [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)；不过，目前我们还不知道 Firefox 上哪个获取 cookies.txt 的插件才是最好的，您可以自行尝试。

<br>

# 使用方法

<p align="center"><img src="https://i.imgur.com/PdT16Hk.png"></p>

1. 通过浏览器扩展导出 cookies.txt。
2. 将界面上要求的信息输入进去，然后点击<b>“获取信息”按钮</b>。
3. 当漫画信息获取完毕后，点击<b>“下载”按钮</b>。

有时候，您只需要下载漫画中的一部分，而不想下载整部漫画。所以，您可以在“下载选项”中设置您要下载的页码范围。比如：

- 只下载第 12 页这一张图：`12`
- 下载第 1 页、第 2 至 10 页（包括第 10 页）、第 12 页：`1, 2-10, 12`
- 下载第 10 至 20 页（包括第 20 页）、第 50 到 60 页（包括第 60 页）：`10-20, 50-60`

<br>

# 开发指南：直接运行本项目

本项目只提供 Windows 下的可执行文件，所以您如果不使用 Windows，可能需要手动运行本项目。本项目是用 Python 写的，项目中的代码不过就是一些 Python 代码而已。所以，您完全可以自己用原版 Python 解释器来运行本项目。

您需要使用 Python 3.9 或以上的版本。

- 首先，运行命令 `pip install -r requirements.txt`，安装所需的依赖。
  - 我们建议您使用 `venv`，因为依赖里有很多用不到的东西。
- 然后，运行`main.py`。

<br>

# 开发指南：自己打包 exe 文件

本项目所发布的 exe 程序是用  **PyInstaller** 打包的。在打包的时候，我们用到了这些参数：

```shell
pyinstaller --onefile --windowed --icon assets/logo-icon.ico --name ComicFuz-Downloader-GUI main.py
```

如果您想自己打包 exe 文件，那么您就需要安装 PyInstaller 和本项目所需的所有依赖包。本项目所需要的所有依赖包，包括 PyInstaller，已经全部定义在 `requirements.txt` 里了。因此，我们建议您在 `venv` 中运行 `pip install -r requirements.txt` 命令来安装所需依赖，然后使用上述命令来打包可执行文件。
