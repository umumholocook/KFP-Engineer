from PIL import Image, ImageSequence
from resource.data.rick_roll import POSITION
import os, io, tempfile

from common.Util import Util

class RickrollGenerator():
    _avatar_size = 94

    def getRickrollPath():
        return os.sep.join((os.getcwd(), "resource", "image", "rickroll", "rick.gif"))
    
    def _getMaskImagePath():
        return os.sep.join((os.getcwd(), "resource", "image", "rickroll", "mask.png"))

    def getRickrollOutPath():
        return os.sep.join((tempfile.gettempdir(), "rickrolled.gif"))

    def createGif(img: Image):
        avatar = img.resize((RickrollGenerator._avatar_size, RickrollGenerator._avatar_size))
        avatar = Util.createCircle(avatar, RickrollGenerator._getMaskImagePath())
        avatar = Util.enlargeImage(avatar)
        rick = Image.open(RickrollGenerator.getRickrollPath())
        frames = []
        index = 0
        for frame in ImageSequence.Iterator(rick):
            x = POSITION[index]["x"]
            y = POSITION[index]["y"]
            d = POSITION[index]["degree"]
            avatarR = Util.rotateImage(avatar, d)
            frame = frame.convert("RGBA")
            frame.paste(avatarR, (x - int(RickrollGenerator._avatar_size / 2 + 20), y - int(RickrollGenerator._avatar_size / 2 + 20)), avatarR)

            b = io.BytesIO()
            frame.save(b, format="GIF")
            frame = Image.open(b)

            frames.append(frame)
            index += 1
        frames[0].save(RickrollGenerator.getRickrollOutPath(), save_all=True, append_images=frames[1:])
        return RickrollGenerator.getRickrollOutPath()