import asyncio
from contextlib import asynccontextmanager
import functools as fntl
from tempfile import TemporaryDirectory
from pathlib import Path

import imgkit

from settings.IMGKitSetting import CONFIG, CACHE_DIR

_OPTIONS = {
    'cache-dir': Path(CACHE_DIR).absolute() / 'HTMLPainter',
    'disable-javascript':  '',
    'log-level': 'warn',
    'transparent': '',
}
if 'xvfb' in CONFIG:
    _OPTIONS['xvfb'] = ''
CONFIG = imgkit.config(**CONFIG)

@asynccontextmanager
async def paint(html, *, allowpaths=[], quality=None, width=None, zoom=None):
    '''
    
    Param:
        html: 欲渲染的 HTML
        allowpaths: 指定 wkhtmltoimage 可存取的本地路徑
        quality: .png 下，不會造成圖片不清楚，越低無損壓縮程度越大
        width: witdh 是輸出的圖像寬度，有縮放的話， width 不會跟著放大
        zoom: 會大感覺畫質會越好

    '''
    with TemporaryDirectory() as outputdir:
        outputpath = Path(outputdir) / 'htmlpainterout.png'
        options = _OPTIONS.copy()
        if len(allowpaths):
            options['allow'] = allowpaths
        if quality is not None:
            options['quality'] = quality
        if width is not None:
            options['width'] = width
        if zoom is not None:
            options['zoom'] = zoom
        loop = asyncio.get_running_loop()
        executor = fntl.partial(imgkit.from_string,
                                html, outputpath, options, config=CONFIG)
        await loop.run_in_executor(None, executor)
        with outputpath.open('rb') as imgfp:
            yield imgfp