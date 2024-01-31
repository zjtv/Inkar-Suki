"""
@description: 用于使用playwright组件（浏览器模拟型爬虫）将网页转换为截图
@date: 2023-07-25
"""
import os
import time
import threading
import uuid
from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger
from sgtpyutils.timer import create_timer
from src.tools.utils import *
import asyncio


def get_uuid():
    return str(uuid.uuid1()).replace("-", "")


class PlaywrightRunner(threading.Thread):
    match_chars = re.compile(r"[a-z|A-Z|0-9| |_|\-|\+|\.]+")

    def with_timestamp(raw_name: str) -> str:
        filename = f"{DateTime().tostring(DateTime.Format.DEFAULT_MIL)}{raw_name}"
        filename = str.join("_", PlaywrightRunner.match_chars.findall(filename))
        return filename

    def convert_filename(url: str) -> str:
        file_url = url.replace(Path(bot_path.CACHE).as_uri(), "")[1:]
        file_url = str.join("_", PlaywrightRunner.match_chars.findall(file_url))
        file_url = file_url[0:124]
        return file_url

    def __init__(self) -> None:
        self.tasks: list[tuple[str, str, bool, int, asyncio.Future]] = []
        self.IsRunning = True
        self._player = None
        self.locker = threading.Lock()
        super().__init__(daemon=True)

    async def init(self):
        player = await async_playwright().start()
        browser = await player.chromium.launch(headless=True, slow_mo=0)
        page = await browser.new_page()
        return page

    def stop(self):
        self.IsRunning = False
        for x in self.tasks:
            x[4].set_exception("thread stopped")

    def run(self):
        ext.SyncRunner.as_sync_method(self.run_loop_async())
        return super().run()

    async def run_loop_async(self):
        while self.IsRunning:
            await self.run_async()
            await asyncio.sleep(0.1)
        logger.warning("rendering thread stopped.")

    async def run_async(self) -> None:
        if self._player is None:
            logger.warning("loading player")
            self._player = await self.init()
            logger.warning(f"completed load player:{self._player}")

        if len(self.tasks) == 0:
            return

        task = self.tasks.pop()
        url, locate, first, delay, future = task
        logger.info(f"rendering start new task:[{url}]")
        player = self._player
        loc = player

        file_url = PlaywrightRunner.convert_filename(url)

        img = f"{bot_path.CACHE}{os.sep}{file_url}.png"
        try:
            await player.goto(url)
            if delay > 0:
                await asyncio.sleep(delay / 1000)

            loc = loc.locator(locate)
            if first:
                loc = loc.first
            await loc.screenshot(path=img)

            def callback(img: str):
                future.set_result(img)
            future.get_loop().call_soon_threadsafe(callback, img)
        except Exception as ex:
            reason = f"图片[{url}]生成失败，请尝试执行`playwright install`！:{ex}"
            logger.warning(reason)
            future.set_exception(ex)
            raise ex

    async def generate_by_url(self, url: str, locate: str = None, first: bool = False, delay: int = 0) -> str:
        t = create_timer()
        t.start()
        future = asyncio.Future()
        self.locker.acquire()
        if not locate and "http:" in url:
            # 网页未启用定位时，截图整个页面
            locate = "div"
            first = True
        self.tasks.append([url, locate, first, delay, future])
        self.locker.release()
        result = await future
        logger.info(f"completed image render [{url}] to [{result}],spent:{t.spent:.2f}s")
        return result


__client = PlaywrightRunner()
__client.start()


def stop_playwright():
    __client.stop()


async def generate_by_url(url: str, locate: str = None, first: bool = False, delay: int = 0):
    result = await __client.generate_by_url(url, locate, first, delay)
    return result


async def generate_by_raw_html(html: str, web: bool = False, locate: str = None, first: bool = False, delay: int = 0, name: str = None):
    if name is None:
        name = get_uuid()
    name = PlaywrightRunner.with_timestamp(name)
    file_path = f"{bot_path.CACHE}{os.sep}{name}.html"
    with open(file_path, "w") as f:
        f.write(html)
    return await generate(file_path, web, locate or "section", first, delay)


async def generate(html: str, web: bool = False, locate: str = None, first: bool = False, delay: int = 0):
    """
    生成指定路径下html文件的截图
    @param html: html文件路径
    @param web: 仅可填False，否则返回空
    @param locate: 填写指定标签以仅截图该标签
    @param first: 是否选取首个元素截图
    @param delay: 打开网页后延迟时间，单位ms
    @return : 返回生成的图片路径
    """
    file_uri = html if web else Path(html).as_uri()
    result = await generate_by_url(file_uri, locate, first, delay)
    if result is None:
        return False
    return result
