import io
import common.database_API as database_API
from PIL import Image, ImageEnhance, ImageFont, ImageDraw

class ProfileObject():
    def __init__(
        self, icon_jpg:bytes, display_name:str, 
        user_neme:str, rank_num:int, rank_:int, 
        coin:int, exp:int, banner_jpg:bytes):
        self.display_name = display_name
        self.user_name = user_neme
        self.rank_num = rank_num
        self.rank_ = rank_
        self.image = Image.new('RGBA', (934,282), (0, 0, 0, 0))
        if banner_jpg != None:
            self.set_background(banner_jpg)
        self.set_base_model()
        if icon_jpg != None:
            self.past_icon(icon_jpg)
        self.coin_num = coin
        self.xp_num = exp
        self.set_member_text()
        self.set_rank_text()
        self.set_xp_progress_and_coin_num()
    
    def set_background(self, data):
        image_bk =  Image.open(io.BytesIO(data))
        re_bk = image_bk.resize((934, int(934*image_bk.size[1]/image_bk.size[0])), Image.ANTIALIAS)
        t_pos = (re_bk.size[1]-282)/2 if (re_bk.size[1]-282)/2 > 0 else (282-re_bk.size[1])/2
        re_bk = re_bk.crop((0, t_pos, re_bk.size[0], re_bk.size[1]))
        image_bk.close()
        self.image.paste(re_bk, (0,0))
        re_bk.close()
    
    def set_base_model(self):
        image_base = Image.open(r"./resource/image/card_base.png")
        if image_base.mode != 'RGBA':
            image_base_rgba=image_base.convert('RGBA')
            image_base.close()
        else:
            image_base_rgba= image_base
        alpha = image_base_rgba.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        image_base_rgba.putalpha(alpha)
        self.image=Image.composite(image_base_rgba, self.image, image_base_rgba)
    
    def past_icon(self, data):
        image_icon=Image.open(io.BytesIO(data))
        self.image.paste(image_icon.resize((142,142)), (60, 70))
        image_icon.close()
    
    def set_member_text(self):
        member_name_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=46,encoding='utf-8')
        user_name_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=27,encoding='utf-8')
        draw = ImageDraw.Draw(self.image)
        draw.text((250,110), self.display_name, font=member_name_font)
        draw.text((250+draw.textsize(self.display_name, font=member_name_font)[0]+20, 110+24), '('+self.user_name+')', font=user_name_font, fill='#ADADAD')
    
    
    def set_rank_text(self):
        draw = ImageDraw.Draw(self.image)
        level_1_text = '等級'
        level_1_size =  26
        level_1_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=level_1_size,encoding='utf-8')

        level_2_text = str(self.rank_)
        level_2_size = 48
        level_2_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=level_2_size,encoding='utf-8')

        rank_1_text = '排名'
        rank_1_size = 26
        rank_1_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=rank_1_size,encoding='utf-8')

        rank_2_text = '#'+str(self.rank_num)
        rank_2_size = 48
        rank_2_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=rank_2_size,encoding='utf-8')

        x_base = 934 - 60
        x_base -= draw.textsize(level_2_text, font=level_2_font)[0]
        draw.text((x_base, 48), level_2_text, font=level_2_font ,fill='#FF0000')
        x_base -= (draw.textsize(level_1_text, font=level_1_font)[0] + 5)
        draw.text((x_base, 70), level_1_text, font=level_1_font ,fill='#FF0000')
        x_base -= (draw.textsize(rank_2_text, font=rank_2_font)[0]+15)
        draw.text((x_base, 48), rank_2_text, font=rank_2_font )
        x_base -= (draw.textsize(rank_1_text, font=rank_1_font)[0]+10)
        draw.text((x_base, 70), rank_1_text, font=rank_1_font )

    def set_xp_progress_and_coin_num(self):
        draw = ImageDraw.Draw(self.image)
        common_size = 27
        common_font = ImageFont.truetype(font=r'./resource/ttf/NotoSansCJKtc-Regular.otf', size=common_size, encoding='utf-8')
        
        text_list_1 = ('硬幣:', str(self.coin_num))
        text_list_fill_1 = ('#E1E100', '#F9F900')[::-1]
        text_list_2 = (str(self.xp_num), '/', str(database_API.calcuelate_xp(self.rank_ + 1)), 'XP')
        text_list_fill_2 = ('#FFFFFF', '#ADADAD', '#ADADAD', '#ADADAD')[::-1]

        x_base = 934 - 60 - 30
        y = 171+15
        for i,t in enumerate(text_list_2[::-1]):
            offset = draw.textsize(t, font=common_font)
            x_base -= (offset[0]+5)
            draw.text((x_base, y), t, fill=text_list_fill_2[i], font=common_font)
        x_base -= 15
        for i,t in enumerate(text_list_1[::-1]):
            offset = draw.textsize(t, font=common_font)
            x_base -= (offset[0]+5)
            draw.text((x_base, y), t, fill=text_list_fill_1[i], font=common_font)