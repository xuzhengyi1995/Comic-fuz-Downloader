__all__ = (
    'MainForm',
)

import functools
import re, os
import threading
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as tkmsg
import tkinter.ttk as ttk
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from queue import Queue, Empty as QueueEmptyError
from threading import Thread
from tkinter.scrolledtext import ScrolledText
from typing import Tuple, Mapping, Any, Sequence, Optional

from validators.url import url as validate_url

from ..constant import *
from ..definition import *
from ..i18n import *
from ..service import *
from ..util import *

RE_PAGE_RANGE = re.compile(r'(\d+|\d+-\d+)(,(\d+|\d+-\d+))*')
RE_SPACE = re.compile(r'\s+')

MESSAGE_BOX_MAX_LENGTH = 128

@dataclass
class ImageDownloadTask:
    # Indicate information of a file
    file_item: ComicFuzFileItem
    license: ComicFuzLicense

    # Used to construct a HttpUtil
    http_util_param: Tuple[Path, str]

    # Save file to this folder
    save_to_path: Path

    # Save image file to this file path
    save_image_file: Optional[Path]

    # Number of page, for logging
    page_num: int

    # Downloaded image
    image_bytes: Optional[bytes]


class MainForm:

    def __init__(self, gui_config: GuiConfig, icon_path: str):
        # >>> Initialize class <<<
        self.num_total_task, self.num_task_finished, self.num_task_succeed = 0, 0, 0
        self.fuz_license, self.fuz_config_pack, self.fuz_url_info, self.fuz_file_items = None, None, None, None

        self.__gui_config = gui_config
        I18nUtil.set_language(gui_config['language'])
        self.__should_restart_me = False

        # >>> Initialize Queue, Timer and threading utils <<<
        self.download_thread_pool: Optional[ThreadPoolExecutor] = None
        self.descramble_thread_pool: Optional[ThreadPoolExecutor] = None
        self.local_http_util: threading.local = None
        self.queue: "Queue[DelegatedTask]" = Queue()

        # >>> Initialize GUI <<<
        self.win = tk.Tk()
        self.win.grid_columnconfigure(0, weight=1)
        self.win.title(tr('Comic FUZ Manga Downloader GUI'))
        self.win.minsize(width=700, height=400)

        if icon_path:
            self.win.iconbitmap(icon_path)

        menu = tk.Menu()

        # Language menu
        submenu = tk.Menu(tearoff=0)
        for i in LANGUAGES:
            submenu.add_command(label=i, command=functools.partial(self.switch_language, to=i))
        menu.add_cascade(label=tr('Langauge'), menu=submenu)

        # About menu
        submenu = tk.Menu(tearoff=0)
        submenu.add_command(label=tr('About'), command=self.about_me)
        menu.add_cascade(label=tr('Help'), menu=submenu)
        self.win['menu'] = menu

        frame = ttk.LabelFrame(self.win, text=tr('Download Settings'), padding=(10, 5, 10, 5))
        frame.grid(row=0, column=0, sticky='we', padx=15, pady=10)
        frame.grid_columnconfigure(1, weight=1)
        for row_index in range(5):
            frame.grid_rowconfigure(row_index, pad=3)

        # Row
        label = ttk.Label(frame, text=tr('Manga URL:'))
        label.grid(row=0, column=0, sticky='e')
        self.manga_url = tk.StringVar(value=gui_config['manga_url'])
        ttk.Entry(frame, textvariable=self.manga_url).grid(row=0, column=1, sticky='we', padx=10)

        # Row
        label = ttk.Label(frame, text=tr('Cookies.txt path:'))
        label.grid(row=1, column=0, sticky='e')
        self.cookie_path = tk.StringVar(value=gui_config['cookie_txt_path'])
        self.txt_cookie_path = ttk.Entry(frame, textvariable=self.cookie_path)
        self.txt_cookie_path.grid(row=1, column=1, sticky='we', padx=10)
        btn = ttk.Button(frame, text=tr('Browse...'), command=self.browse_cookie_path)
        btn.grid(row=1, column=2)

        # Row
        label = ttk.Label(frame, text=tr('Save to:'))
        label.grid(row=2, column=0, sticky='e')
        self.output_path = tk.StringVar(value=gui_config['save_to_path'])
        self.txt_output_path = ttk.Entry(frame, textvariable=self.output_path)
        self.txt_output_path.grid(row=2, column=1, sticky='we', padx=10)
        btn = ttk.Button(frame, text=tr('Browse...'), command=self.browse_output_path)
        btn.grid(row=2, column=2)

        # Row
        label = ttk.Label(frame, text=tr('Proxy:'))
        label.grid(row=3, column=0, sticky='e')
        sub_frame = ttk.Frame(frame)
        sub_frame.grid(row=3, column=1, sticky='w', padx=10)
        self.proxy_state = tk.StringVar(value='disabled')
        ttk.Radiobutton(
            sub_frame, text=tr('[Proxy] Disabled'), value='disabled',
            variable=self.proxy_state, command=self.proxy_radiobutton_clicked,
        ).grid(row=0, column=0)
        ttk.Radiobutton(
            sub_frame, text=tr('[Proxy] HTTP'), value='http',
            variable=self.proxy_state, command=self.proxy_radiobutton_clicked,
        ).grid(row=0, column=1)
        ttk.Radiobutton(
            sub_frame, text=tr('[Proxy] SOCKS5'), value='socks5',
            variable=self.proxy_state, command=self.proxy_radiobutton_clicked,
        ).grid(row=0, column=2, padx=(0, 20))
        self.proxy_host = tk.StringVar()
        self.proxy_host_txt = ttk.Entry(sub_frame, textvariable=self.proxy_host, state='disabled')
        self.proxy_host_txt.grid(row=0, column=3)
        ttk.Label(sub_frame, text=':').grid(row=0, column=4)
        self.proxy_port = tk.StringVar()
        self.proxy_port_txt = ttk.Entry(sub_frame, textvariable=self.proxy_port, width=6, state='disabled')
        self.proxy_port_txt.grid(row=0, column=5)

        # Row
        label = ttk.Label(frame, text=tr('Threads num:'))
        label.grid(row=4, column=0, sticky='e')
        self.spin_threads = ttk.Spinbox(
            frame, values=tuple(range(1, MAX_THREAD_LIMIT + 1)), width=15, validate='all'
        )
        self.spin_threads.set(gui_config['thread_num'])
        self.spin_threads.grid(row=4, column=1, sticky='w', padx=10, pady=(3, 0))

        # Row
        frame = ttk.Frame(self.win, padding=(15, 0, 15, 10))
        frame.grid(row=1, column=0, sticky='we')
        frame.grid_columnconfigure(0, weight=1)

        self.manga_info_frame = ttk.LabelFrame(frame, text=tr('Manga Info'), padding=(10, 5, 10, 10))
        self.manga_info_frame.grid(row=1, column=0, sticky='news', padx=(0, 15), pady=0)
        self.manga_info_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.manga_info_frame, text=tr('Title:')).grid(row=0, column=0, sticky='e', padx=(0, 5))
        self.manga_title = ttk.Label(self.manga_info_frame, width=60)
        self.manga_title.grid(row=0, column=1, sticky='w')

        ttk.Label(self.manga_info_frame, text=tr('Page num:')).grid(row=1, column=0, sticky='e', padx=(0, 5))
        self.manga_page_num = ttk.Label(self.manga_info_frame, width=10)
        self.manga_page_num.grid(row=1, column=1, sticky='w')

        self.download_option_frame = ttk.LabelFrame(frame, text=tr('Download Options'), padding=(10, 5, 10, 10))
        self.download_option_frame.grid(row=1, column=1, sticky='news')

        ttk.Label(
            self.download_option_frame, text=tr('[Download Options] Range:')
        ).grid(row=0, column=0, sticky='e', padx=(0, 5))
        self.range_option = tk.StringVar(value='all')
        ttk.Radiobutton(
            self.download_option_frame, text=tr('[Download Options] All'), variable=self.range_option, value='all',
            command=self.range_option_clicked,
        ).grid(row=0, column=1)
        ttk.Radiobutton(
            self.download_option_frame, text=tr('[Download Options] Partition'), variable=self.range_option,
            value='part',
            command=self.range_option_clicked,
        ).grid(row=0, column=2)
        ttk.Label(
            self.download_option_frame, text=tr('[Download Options] Pages:')
        ).grid(row=1, column=0, sticky='e', padx=(0, 5))
        self.download_page_range = tk.StringVar()
        self.txt_download_page_range = ttk.Entry(
            self.download_option_frame, textvariable=self.download_page_range, state='disabled')
        self.txt_download_page_range.grid(row=1, column=1, columnspan=2, sticky='we')

        # Row
        frame = ttk.Frame(self.win)
        frame.grid(row=2, column=0, sticky='we', padx=15, pady=0)
        frame.grid_columnconfigure(0, weight=1)

        self.progress_indicator = tk.IntVar()
        progress_bar = ttk.Progressbar(
            frame, mode='determinate', orient=tk.HORIZONTAL, variable=self.progress_indicator)
        progress_bar.grid(row=0, column=0, sticky='news', pady=1, padx=(0, 10))
        self.fetch_btn = ttk.Button(frame, text=tr('Fetch'), command=self.fetch_btn_clicked)
        self.fetch_btn.grid(row=0, column=1, padx=(0, 5))
        self.download_btn = ttk.Button(frame, text=tr('Download'), state='disabled', command=self.download_btn_clicked)
        self.download_btn.grid(row=0, column=2, padx=(0, 5))
        self.cancel_btn = ttk.Button(frame, text=tr('Cancel'), state='disabled', command=self.cancel_btn_clicked)
        self.cancel_btn.grid(row=0, column=3)

        self.scroll_text = ScrolledText(self.win, height=10, state='disabled')
        self.scroll_text.grid(row=3, column=0, sticky='news', padx=15, pady=(10, 15))

        self.win.grid_rowconfigure(3, weight=1)

        # >>> Initialize logging system <<<
        self.scroll_text.tag_config('verbose', foreground='#808080')
        self.scroll_text.tag_config('info', foreground='#449944')
        self.scroll_text.tag_config('error', foreground='#e25252')

        # Initial log, to solve the `Invalid index` issue
        self.scroll_text.insert(tk.INSERT, tr('Welcome to use the downloader.'), 'verbose')

    def about_me(self):
        tkmsg.showinfo(title=tr('[MessageBox] About'), message=tr('[MessageBox] [About Message]'), parent=self.win)

    def main_loop(self) -> Tuple[GuiConfig, bool]:
        """
        Launch the main loop.
        return: (gui_config, should_restart_me)
            - The first element records latest GUI config.
            - The second element indicates requesting outer code to show a new form instead of exit program.
        """
        # Start delegation queue
        self.win.after(QUEUE_CHECKING_DELAY, self.regularly_check_queue)

        self.win.mainloop()

        # Remember settings
        self.__gui_config['cookie_txt_path'] = self.cookie_path.get().strip()
        self.__gui_config['manga_url'] = self.manga_url.get().strip()
        self.__gui_config['save_to_path'] = self.output_path.get().strip()

        return self.__gui_config, self.__should_restart_me

    def __log(self, x: str, log_type: str):
        """
        log_type: one of `verbose`, `info`, `error`.
        """
        self.scroll_text['state'] = 'normal'
        self.scroll_text.insert(tk.END, x + '\n', log_type)
        self.scroll_text['state'] = 'disabled'
        self.scroll_text.see(tk.END)

    def log_verbose(self, x: str) -> None:
        self.__log(x, 'verbose')

    def log_info(self, x: str) -> None:
        self.__log(x, 'info')

    def log_error(self, x: str) -> None:
        self.__log(x, 'error')

    def regularly_check_queue(self) -> None:
        while True:
            try:
                task = self.queue.get_nowait()
            except QueueEmptyError:
                break

            task.func(*task.args, **task.kwargs)

        self.win.after(QUEUE_CHECKING_DELAY, self.regularly_check_queue)

    def proxy_radiobutton_clicked(self) -> None:
        if self.proxy_state.get() == 'disabled':
            self.proxy_host_txt['state'] = 'disabled'
            self.proxy_port_txt['state'] = 'disabled'
        else:
            self.proxy_host_txt['state'] = 'normal'
            self.proxy_port_txt['state'] = 'normal'

    def cookie_path_change(self):
        self.__gui_config['cookie_txt_path'] = self.cookie_path.get()

    def browse_cookie_path(self):
        result = filedialog.askopenfilename(
            parent=self.win,
            title=tr('Select cookies.txt...'),
            filetypes=[(tr('Text files'), '*.txt')],
        )
        if result:
            result = str(Path(result).resolve(strict=False))
            self.cookie_path.set(result)

    def browse_output_path(self):
        result = filedialog.askdirectory(
            parent=self.win,
            title=tr('Select output directory...'),
        )
        if result:
            result = str(Path(result).resolve(strict=False))
            self.output_path.set(result)

    def range_option_clicked(self):
        state_mapping = {
            'all': 'disabled',
            'part': 'normal',
        }
        self.txt_download_page_range['state'] = state_mapping[self.range_option.get()]

    def switch_language(self, to: str) -> None:
        if self.__gui_config['language'] == to:
            return

        self.__should_restart_me = True
        self.__gui_config['language'] = to
        self.win.destroy()

    def check_fetch_settings(self) -> bool:
        self.get_and_correct_spin_thread_num()

        if validate_url(self.manga_url.get()) is not True:
            self.log_and_show_error(tr('The URL in the Manga URL field is invalid.'))
            return False

        if not Path(self.cookie_path.get()).exists():
            self.log_and_show_error(tr('The cookies.txt does not exist at the given path.'))
            return False

        if self.proxy_state.get() != 'disabled':
            if self.proxy_host.get().strip() == '':
                self.log_and_show_error(tr('Invalid proxy host name.'))
                return False

            try:
                proxy_port = int(self.proxy_port.get())
                if proxy_port > 65535 or proxy_port < 1:
                    raise RuntimeError()
            except:
                self.log_and_show_error(tr('Invalid proxy port.'))
                return False

        return True

    def is_download_range_correct(self) -> bool:
        download_range = self.download_page_range.get()
        download_range = RE_SPACE.sub('', download_range)
        return bool(RE_PAGE_RANGE.fullmatch(download_range))

    def check_download_settings(self) -> bool:
        if not self.check_fetch_settings():
            return False

        if self.output_path.get().strip() == '':
            self.log_and_show_error(tr('The download directory is not specified.'))
            return False

        if self.range_option.get() == 'part' and not self.is_download_range_correct():
            self.log_and_show_error(tr('You chose to download part of mangas, '
                                       'but you did not specify correct page ranges.'))
            return False

        return True

    def get_and_correct_spin_thread_num(self) -> int:
        try:
            thread_num = int(self.spin_threads.get())
            if thread_num < 1:
                thread_num = 1
            elif thread_num > MAX_THREAD_LIMIT:
                thread_num = MAX_THREAD_LIMIT
        except:
            thread_num = DEFAULT_THREAD_NUM

        self.spin_threads.set(thread_num)
        return thread_num

    def log_and_show_error(self, error_msg: str) -> None:
        self.log_error(error_msg)
        tkmsg.showerror(title=tr('[MessageBox] Error'), message=error_msg[:MESSAGE_BOX_MAX_LENGTH], parent=self.win)

    def get_proxy_url(self):
        proxy_scheme = self.proxy_state.get().strip()
        if proxy_scheme == 'disabled':
            return ''

        return f'{proxy_scheme}://{self.proxy_host.get().strip()}:{self.proxy_port.get().strip()}'

    def clear_manga_info(self):
        self.manga_title['text'] = ''
        self.manga_page_num['text'] = ''
        self.fetch_btn['state'] = 'disabled'
        self.download_btn['state'] = 'disabled'

    def cancel_btn_clicked(self) -> None:
        self.clear_manga_info()
        if self.download_thread_pool is not None:
            self.log_verbose(tr('Canceling...'))
            self.reset_download_state()

        self.cancel_btn['state'] = 'disabled'

    def fetch_btn_clicked(self) -> None:
        if not self.check_fetch_settings():
            return

        self.log_verbose(tr('Fetching manga info...'))
        try:
            url_info = ComicFuzUrlParser.parse(self.manga_url.get())
        except:
            traceback.print_exc()
            self.log_and_show_error(
                tr('Unable to parse Comic FUZ URL. You should specify the URL of the page that reads manga.'))
            return

        self.clear_manga_info()

        self.fuz_url_info = url_info
        Thread(
            target=self.thr_fetch_manga_info,
            args=(HttpUtil(Path(self.cookie_path.get()), self.get_proxy_url()), self.fuz_url_info),
            name='FetchMangaInfo',
        ).start()

    def fetch_manga_info_finished(
            self, license: ComicFuzLicense, config_pack: Mapping[str, Any], file_items: Sequence[ComicFuzFileItem],
    ):
        self.fuz_license = license
        self.fuz_config_pack = config_pack
        self.fuz_file_items = file_items

        self.manga_title['text'] = self.fuz_url_info.manga_name
        self.manga_page_num['text'] = len(file_items)

        self.download_btn['state'] = 'normal'
        self.fetch_btn['state'] = 'normal'

        self.log_info(tr('Manga info fetched. Ready to download.'))

    def thr_fetch_manga_info_failed(self, reason: str):
        self.log_and_show_error(tr('Failed to fetch manga info. The traceback is listed below.\n{}').format(reason))
        self.fetch_btn['state'] = 'normal'

    def thr_fetch_manga_info(
            self, http_util: HttpUtil, manga_url_info: ComicFuzUrlInfo
    ) -> None:
        try:
            license, config_pack = ComicFuzService.get_license_and_cfg_pack(manga_url_info, http_util)
            file_items = CfgPackParser.parse(config_pack)
        except:
            traceback.print_exc()
            self.queue.put(DelegatedTask(
                func=self.thr_fetch_manga_info_failed,
                args=(traceback.format_exc(),)
            ))
            return

        self.queue.put(DelegatedTask(
            func=self.fetch_manga_info_finished,
            args=(license, config_pack, file_items),
        ))

    def get_save_to_path(self) -> Path:
        save_to_path = Path(self.output_path.get().strip())
        if save_to_path.exists():
            if not save_to_path.is_dir():
                raise RuntimeError('The save_to_path exists but is not a directory.')
        else:
            os.makedirs(save_to_path, exist_ok=True)

        return save_to_path

    def parse_download_range(self) -> Sequence[Tuple[int, int]]:
        range_option = self.range_option.get()
        if range_option == 'all':
            return [(1, len(self.fuz_file_items) + 1)]

        page_range_str = self.download_page_range.get()
        page_ranges = RangeUtil.parse_range_string(
            page_range_str, right_open=False, bounding_range=(1, len(self.fuz_file_items) + 1))
        page_ranges = RangeUtil.merge_ranges(page_ranges)

        return page_ranges

    def thr_download_image(self, task: ImageDownloadTask):
        try:
            http_util = getattr(self.local_http_util, 'http_util', None)
            if http_util is None:
                http_util = HttpUtil(*task.http_util_param)
                self.local_http_util.http_util = http_util

            task.save_image_file = (task.save_to_path / f'{task.file_item.file_disk_name}.png')
            if task.save_image_file.exists():
                self.queue.put(DelegatedTask(
                    func=self.download_image_finished, args=(True, task.page_num)
                ))
                return

            task.image_bytes = ComicFuzService.get_image(task.file_item.file_path, task.license, http_util)
            self.descramble_thread_pool.submit(
                self.thr_descramble_image, task
            )
        except:
            traceback.print_exc()
            self.queue.put(DelegatedTask(
                func=self.download_image_finished, args=(False, task.page_num)
            ))

    def thr_descramble_image(
            self, task: ImageDownloadTask,
    ) -> None:
        try:
            pattern = ScrambleCalculator.pattern(task.file_item)
            descrambled = ImageDescrambler.descramble_image(task.image_bytes, pattern, task.file_item.dummy_pixels)
            task.save_image_file.write_bytes(descrambled)

            self.queue.put(DelegatedTask(
                func=self.download_image_finished, args=(True, task.page_num)
            ))
        except:
            traceback.print_exc()
            self.queue.put(DelegatedTask(
                func=self.download_image_finished, args=(False, task.page_num)
            ))

    def download_image_finished(self, succeed: bool, page_num: int):
        self.num_task_finished += 1
        if succeed:
            self.num_task_succeed += 1

        if self.num_total_task == 0:
            progress = 0
        else:
            progress = int(self.num_task_finished / self.num_total_task * 100)
        self.progress_indicator.set(progress)

        if succeed:
            self.log_verbose(tr('Page {page} successfully downloaded.').format(page=page_num))
        else:
            self.log_error(tr('Failed to download page {page}.').format(page=page_num))

        if self.num_task_finished >= self.num_total_task:
            self.reset_download_state()

            self.log_info(tr('Manga download finished. {succeed} succeed and {failed} failed.').format(
                succeed=self.num_task_succeed, failed=self.num_total_task - self.num_task_succeed
            ))

    def thr_reset_download_state(self):
        self.download_thread_pool.shutdown(wait=True, cancel_futures=True)
        self.download_thread_pool = None
        self.descramble_thread_pool.shutdown(wait=True, cancel_futures=True)
        self.descramble_thread_pool = None
        self.local_http_util = None

        self.queue.put(DelegatedTask(
            func=self.reset_download_state_finished,
        ))

    def reset_download_state_finished(self):
        self.spin_threads['state'] = 'normal'
        self.fetch_btn['state'] = 'normal'
        self.download_btn['state'] = 'normal'
        self.cancel_btn['state'] = 'disabled'

    def reset_download_state(self):
        Thread(target=self.thr_reset_download_state, name='Shutdown-thread-pool').start()

    def download_btn_clicked(self) -> None:
        if not self.check_download_settings():
            return

        try:
            save_to_path = self.get_save_to_path()
        except:
            traceback.print_exc()
            self.log_and_show_error(tr('The images can not be saved to the specified path.'))
            return

        download_range = self.parse_download_range()
        self.num_total_task, self.num_task_finished, self.num_task_succeed = 0, 0, 0
        for a, b in download_range:
            self.num_total_task += b - a

        self.download_thread_pool = ThreadPoolExecutor(max_workers=int(self.spin_threads.get()))
        self.descramble_thread_pool = ThreadPoolExecutor(max_workers=max(MAX_CPU_THREAD, os.cpu_count()))
        self.local_http_util = threading.local()

        for a, b in download_range:
            for i in range(a, b):
                task = ImageDownloadTask(
                    file_item=self.fuz_file_items[i - 1],
                    license=self.fuz_license,
                    http_util_param=(Path(self.cookie_path.get()), self.get_proxy_url()),
                    save_to_path=save_to_path,
                    save_image_file=None,
                    page_num=i,
                    image_bytes=None,
                )
                self.download_thread_pool.submit(
                    self.thr_download_image, task
                )

        self.spin_threads['state'] = 'disabled'
        self.fetch_btn['state'] = 'disabled'
        self.download_btn['state'] = 'disabled'
        self.cancel_btn['state'] = 'normal'
        self.log_verbose(tr('Download begins'))
