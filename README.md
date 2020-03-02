# Comic-fuz Downloader

Download manga you rent from <https://comic-fuz.com/>

# How to Use

0.  Install python packages _pillow_ and _threadpool_.

    ```shell
    pip install Pillow
    pip install threadpool
    ```

1.  Add your cookies in the program.

    **Remember to use F12 to see the cookies!**

    **Because some http only cookies can not be seen by javascript!**

    > 1.  Open the page.
    > 2.  Press F12.
    > 3.  Click on the _Network_.
    > 4.  Refresh the page.
    > 5.  Find the first _viewer.html?cid=XXXXXXXXXXXXX......_ request, click it.
    > 6.  On the right, there will be a _Request Headers_, go there.
    > 7.  Find the _cookie:...._, copy the string after the _cookie:_, paste to the _settings.py_, _YOUR_COOKIES_HERE_

2.  Change the _URL_ in the _settings.py_.

    The URL will have something like **viewer.html?cid=XXXX** in it, here we use the manga [ご注文はうさぎですか？　１巻](https://comic-fuz.com/viewer.html?cid=S00176-k-001&cty=1&cti=%E3%81%94%E6%B3%A8%E6%96%87%E3%81%AF%E3%81%86%E3%81%95%E3%81%8E%E3%81%A7%E3%81%99%E3%81%8B%EF%BC%9F%E3%80%80%EF%BC%91%E5%B7%BB&lin=0&bs=1).

    This is the URL of the **ご注文はうさぎですか？　１巻**: <https://comic-fuz.com/viewer.html?cid=S00176-k-001&cty=1&cti=%E3%81%94%E6%B3%A8%E6%96%87%E3%81%AF%E3%81%86%E3%81%95%E3%81%8E%E3%81%A7%E3%81%99%E3%81%8B%EF%BC%9F%E3%80%80%EF%BC%91%E5%B7%BB&lin=0&bs=1>

    Just copy this URL to the `URL` in _settings.py_.

3.  After edit the program, run `python main.py` to run it, very easy.

# Notice

1.  The `poolsize` by default is 5, it's already fast enough I think, you can change it but be careful that the server may **ban your ip or account** (I'm not sure, but be careful).
