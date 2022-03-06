import os, tempfile, unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common.ImageWithTextPosition import ImageWithTextPosition
from common.Position import Position

# Simple Image generation util
# Right now this class support generating image with characters
class ImageUtil():
    
    def _getTempFileName():
        return "meme.jpg"

    def _getStoragePath():
        return os.sep.join((tempfile.gettempdir(), ImageUtil._getTempFileName()))

    def renderText(text: str, image: ImageWithTextPosition):
        return (ImageUtil._getTempFileName(), ImageUtil._renderText(text, image))

    def _getSubText(text: str, offset: int):
        subText = ""
        length = 0
        for i in range(offset, min(offset + 4, len(text))):
            status = unicodedata.east_asian_width(text[i])
            if status == 'W':
                length += 2    
            else:
                length += 1
            if length > 4:
                break
            subText += text[i] 
        return subText

    def _renderText(text: str, imageInfo: ImageWithTextPosition):
        image = Image.open(imageInfo.image_path)
        draw = ImageDraw.Draw(image)

        subText_1 = ImageUtil._getSubText(text, 0)
        textRenderedSoFar = 0
        if (len(subText_1) > 0):
            if (unicodedata.east_asian_width(subText_1[0]) == 'W'):
                # drawing asian character
                textRenderedSoFar = ImageUtil._drawText(image, draw, subText_1[0], 0, imageInfo)
            else:
                textRenderedSoFar = ImageUtil._drawText(image, draw, subText_1[0::1], 0, imageInfo)
        if ((len(subText_1) - textRenderedSoFar) > 0):
            ImageUtil._drawText(image, draw, subText_1[textRenderedSoFar::], 1, imageInfo)
            
        subText_2 = ImageUtil._getSubText(text, len(subText_1))
        if (len(subText_2) > 0):
            if (unicodedata.east_asian_width(subText_2[0]) == 'W'):
                textRenderedSoFar = ImageUtil._drawText(image, draw, subText_2[0], 2, imageInfo)
            else:
                textRenderedSoFar = ImageUtil._drawText(image, draw, subText_2[0::1], 2, imageInfo)
        if ((len(subText_2) - textRenderedSoFar) > 0):
            ImageUtil._drawText(image, draw, subText_2[textRenderedSoFar::], 3, imageInfo)
        
        image.save(ImageUtil._getStoragePath())

        return ImageUtil._getStoragePath()

    def _drawText(image: Image, draw: ImageDraw, text: str, position: int, imageInfo: ImageWithTextPosition):
        ImageUtil._renderSubTextShadow(imageInfo.charPositions[position], text, image, imageInfo.size, imageInfo.angles[position])
        ImageUtil._renderSubText(imageInfo.charPositions[position], imageInfo.colors[position], text, image, imageInfo.size, imageInfo.angles[position])
        return len(text)

    def _renderSubTextShadow(offset: Position, subText: str, image: Image, size: int, angle: int):
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=size, encoding='utf-8')
        textSize = ImageDraw.Draw(image).textsize(subText, font)

        blurred = Image.new('RGBA', textSize)
        draw = ImageDraw.Draw(blurred)
        size = 1.2
        draw.text((textSize[0] / 2, textSize[1] / 2), subText, fill=(255, 255, 255), font=font, anchor='mm')
        blurred = blurred.resize((int(blurred.size[0] * size), int(blurred.size[1] * size)))
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=2))
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=2))
        white = Image.new('RGBA', blurred.size, (255, 255, 255))
        
        # Paste soft text onto background
        image.paste(white, (offset.x, offset.y), blurred.rotate(angle, False))
    
    # def _renderSubText(offset: Position, text_color, subText: str, draw: ImageDraw, size: int, angle):
    #     stroke_color = (0, 0, 0)
    #     font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=size, encoding='utf-8')
    #     draw.text((offset.x, offset.y), subText, fill=text_color, font=font, stroke_width=2, stroke_fill=stroke_color)
    #     return draw.textsize(subText, font)
    def _renderSubText(offset: Position, text_color, subText: str, image: Image, size: int, angle):
        stroke_color = (0, 0, 0)
        font = ImageFont.truetype(os.sep.join((os.getcwd(), "resource", "ttf", "DFKai-SB.ttf")), size=size, encoding='utf-8')

        textCanvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        textDraw = ImageDraw.Draw(textCanvas)

        textDraw.text((0, 0), subText, fill=text_color, font=font, stroke_width=2, stroke_fill=stroke_color)

        rotatedText = textCanvas.rotate(angle, resample=Image.BILINEAR, expand=True, fillcolor=(0, 0, 0, 0))
        
        image.paste(rotatedText, (offset.x, offset.y), rotatedText)