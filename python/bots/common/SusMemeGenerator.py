from PIL import Image, ImageDraw, ImageFont
from numpy import asarray
import os, tempfile, random, imageio, asyncio


class SusMemeGenerator():

    _avatar_size = 97
    _nameLimit = 15
    _crewmateNameList = [
        "BLACK.png",
        "BLUE.png",
        "BROWN.png",
        "CYAN.png",
        "GRAY.png",
        "GREEN.png",
        "LIME.png",
        "ORANGE.png",
        "PINK.png",
        "PURPLE.png",
        "RED.png",
        "WHITE.png",
        "YELLOW.png",
    ]

    def getMemePath():
        return os.sep.join((tempfile.gettempdir(), "sus.gif"))

    def createGifWithoutAvatar(user_name: str, crewmate_color: str = "random"):
        return SusMemeGenerator.createGif(user_name, None, crewmate_color=crewmate_color)

    def createGif(user_name: str, avatar: Image, crewmate_color: str = "random"):
        if os.path.exists(SusMemeGenerator.getMemePath()):
            os.remove(SusMemeGenerator.getMemePath())
        filenames = []
        
        for index in range(1, 154):
            filenames.append(os.sep.join((os.getcwd(), "resource", "image", "sky", f"{index}.png")))
        text = SusMemeGenerator._getStatusText(user_name)
        crewmate_path = SusMemeGenerator._getCrewmateImagePath(crewmate_color)
        createmate_image = SusMemeGenerator._createCrewmate(crewmate_path, avatar)
        images = []
        for i, filename in enumerate(filenames):
            imageWithCrewmate = SusMemeGenerator._renderCrewmate(filename, createmate_image, i, len(filenames))
            imageWithText = SusMemeGenerator._renderText(text, imageWithCrewmate, i, len(filenames))
            images.append(imageWithText)
        imageio.mimsave(SusMemeGenerator.getMemePath(), images, duration=0.03)


        return SusMemeGenerator.getMemePath()

    def _getStatusText(name: str):
        real_name = name
        if len(name) > SusMemeGenerator._nameLimit:
            real_name = f"{name[0:SusMemeGenerator._nameLimit]}..."
        return f"{real_name} was ejected."
    
    def _createCrewmate(crewmate_path: str, avatar: Image):
        crewmate_original = Image.open(crewmate_path)
        
        if avatar:
            mask = Image.open(SusMemeGenerator._getMaskImagePath()).resize((SusMemeGenerator._avatar_size, SusMemeGenerator._avatar_size))
            img = avatar.resize((SusMemeGenerator._avatar_size, SusMemeGenerator._avatar_size))
            crewmate_original.paste(img, (crewmate_original.size[0] - 95, 0), mask)
        return crewmate_original

    def _renderCrewmate(image_path: str, crewmate: Image, index: int, total: int):
        fly_over_speed = 1.8 # 2 is half of the screen width
        degree = index * 360 / total * -1
        image = Image.open(image_path)
        c_w, c_h = crewmate.size
        crewmate_rotated = crewmate.rotate(degree, expand=True)
        sky_w, sky_h = image.size
        x_offset = -1 * c_w + index * sky_w // total * fly_over_speed
        offset = (int(x_offset), (sky_h - c_h) // 2)
        image.paste(crewmate_rotated, offset)
        return image

    def _getMaskImagePath():
        return os.sep.join((os.getcwd(), "resource", "image", "crewmates", "mask.png"))
    
    def _getCrewmateImagePath(crewmate_color: str):
        if "RANDOM" == crewmate_color:
            return os.sep.join((os.getcwd(), "resource", "image", "crewmates", random.choice(SusMemeGenerator._crewmateNameList)))
        else:
            return os.sep.join((os.getcwd(), "resource", "image", "crewmates", f"{crewmate_color}.png")) 
    
    def _getCurrentText(original: str, index: int, total: int):
        text_end = min(len(original) * max(index - total / 3, 0) * 3 // total, len(original))
        return original[0:int(text_end)]
        
    
    def _renderText(text: str, image: Image, index: int, total: int):
        text_to_render = SusMemeGenerator._getCurrentText(text, index, total)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "NotoSansCJKtc-Regular.otf")), size=70, encoding='utf-8')
        sky_w, sky_h = image.size
        text_w, text_h = draw.textsize(text_to_render, font)
        draw.text(((sky_w - text_w) // 2, (sky_h - text_h) // 2), text_to_render, (255, 255, 255), font=font)
        return asarray(image.resize((768, 432)))
