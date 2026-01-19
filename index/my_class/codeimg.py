import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def check_code(width=150, height=50, char_length=5, font_file='SS.TTF', font_size=32):
    code = []
    # 使用浅色背景
    img = Image.new(mode='RGB', size=(width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img, mode='RGB')

    def rndChar():
        """
        生成随机字母或数字
        """
        # 50%概率生成字母，50%概率生成数字
        if random.random() > 0.5:
            return chr(random.randint(65, 90))  # A-Z
        else:
            return chr(random.randint(48, 57))  # 0-9

    def rndColor():
        """
        生成随机深色，用于文字
        """
        return (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))

    def rndLightColor():
        """
        生成随机浅色，用于干扰元素
        """
        return (random.randint(150, 220), random.randint(150, 220), random.randint(150, 220))

    # 写文字
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        # 减少文字上下偏移范围
        h = random.randint(5, 10)
        # 使用深色文字
        draw.text([i * width / char_length + 10, h], char, font=font, fill=rndColor())

    # 大幅减少干扰点数量
    for i in range(15):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rndLightColor())

    # 大幅减少干扰圆圈数量
    for i in range(10):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 3, y + 3), 0, 90, fill=rndLightColor())

    # 减少干扰线数量并使用浅色
    for i in range(2):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=rndLightColor(), width=1)

    # 使用更柔和的滤镜
    img = img.filter(ImageFilter.SMOOTH)
    return img, ''.join(code)


if __name__ == '__main__':
    img, code_str = check_code()
    print(f"验证码: {code_str}")

    with open('code.png', 'wb') as f:
        img.save(f, format='png')


# 第一版验证码
# import random
# from PIL import Image, ImageDraw, ImageFont, ImageFilter
#
#
# def check_code(width=120, height=30, char_length=5, font_file='SS.TTF', font_size=28):
#     code = []
#     img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
#     draw = ImageDraw.Draw(img, mode='RGB')
#
#     def rndChar():
#         """
#         生成随机字母
#         :return:
#         """
#         return chr(random.randint(65, 90))
#
#     def rndColor():
#         """
#         生成随机颜色
#         :return:
#         """
#         return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))
#
#     # 写文字
#     font = ImageFont.truetype(font_file, font_size)
#     for i in range(char_length):
#         char = rndChar()
#         code.append(char)
#         h = random.randint(0, 4)
#         draw.text([i * width / char_length, h], char, font=font, fill=rndColor())
#
#     # 写干扰点
#     for i in range(40):
#         draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
#
#     # 写干扰圆圈
#     for i in range(40):
#         draw.point([random.randint(0, width), random.randint(0, height)], fill=rndColor())
#         x = random.randint(0, width)
#         y = random.randint(0, height)
#         draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rndColor())
#
#     # 画干扰线
#     for i in range(5):
#         x1 = random.randint(0, width)
#         y1 = random.randint(0, height)
#         x2 = random.randint(0, width)
#         y2 = random.randint(0, height)
#
#         draw.line((x1, y1, x2, y2), fill=rndColor())
#
#     img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
#     return img, ''.join(code)
#
#
# if __name__ == '__main__':
#     img, code_str = check_code()
#     print(code_str)
#
#     with open('code.png', 'wb') as f:
#         img.save(f, format='png')