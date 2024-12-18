#! python3
# -*- coding:utf-8 -*-
# @Author  : berg-1
class Config:
    def __init__(self, output_path, rows=3, cols=3, mode="RGB",
                 font_text="arial.ttf", font_timestamp="arial.ttf", bg_color="#2E2E2E", text_color="#FBFBFDFF",
                 time_color="#FFFFFF99", outline="#00000040",
                 shadow="#12121266", shadow_bg="#2E2E2E", shadow_iter=10):
        self.output = output_path
        self.rows = rows
        self.cols = cols
        self.mode = mode
        self.font_text = font_text
        self.font_timestamp = font_timestamp
        self.bg_color = bg_color
        self.text_color = text_color
        self.time_color = time_color
        self.outline = outline
        self.shadow = shadow
        self.shadow_bg = shadow_bg
        self.shadow_iter = shadow_iter
        self.shrink = 4
        self.shadow_offset = [10, 6]


class OutputFigure:
    def __init__(self, image_width, image_height, config: Config):
        self.rows = config.rows
        self.cols = config.cols
        original_aspect_ratio = image_height / image_width
        if image_width > image_height:
            image_width = nearest_1024_multiple(image_width)
            self.width = int(image_width / config.shrink)
            self.height = int(self.width * original_aspect_ratio)
            self.padding = int(image_width / 32 / config.shrink)
        else:
            image_height = nearest_1024_multiple(image_height)
            self.height = int(image_height / config.shrink)
            self.width = int(self.height / original_aspect_ratio)
            self.padding = int(image_height / 32 / config.shrink)
        self.border = int(self.padding / 4)
        self.fontSize = int(self.width / 16)
        self.lineSpacing = int(self.width / 256)
        self.border = int(self.width / 1024)
        self.shadowBorder = int(self.padding / 4)
        self.w = (self.width + self.padding + self.border * 2) * self.cols + self.padding
        self.h = (self.height + self.padding + self.border * 2) * self.rows
        self.color = Color(bg_color=config.bg_color, text_color=config.text_color, time_color=config.time_color,
                           outline=config.outline, shadow=config.shadow, shadow_bg=config.shadow_bg)
        self.font = Font(font_text=config.font_text, font_timestamp=config.font_timestamp)
        self.shadowOffset = config.shadow_offset

    def __str__(self):
        return f"""\
        width: {self.width}
        height: {self.height}
        padding: {self.padding}
        border: {self.border}
        fontSize: {self.fontSize}
        lineSpacing: {self.lineSpacing}
        border: {self.border}
        shadowBorder: {self.shadowBorder}
        width: {self.w}
        height: {self.h}
        """


class Color:
    def __init__(self, bg_color, text_color, time_color, outline, shadow, shadow_bg):
        self.background = bg_color
        self.text = text_color
        self.timestamp = time_color
        self.outline = outline
        self.shadow = shadow
        self.shadowBg = shadow_bg


class Font:
    def __init__(self, font_text, font_timestamp):
        self.font_text = font_text
        self.font_timestamp = font_timestamp


def nearest_1024_multiple(number, max_size=12288):
    c = round(number / 2048 + 1) * 2048
    if c > max_size:
        return max_size
    return c


def nearest_10000_multiple(number):
    c = round(number / 10000)
    if c < 1:
        return 1
    return c


if __name__ == '__main__':
    _f = OutputFigure(image_width=1960, image_height=1080, config=Config("./"))
    print(_f)

    print(nearest_10000_multiple(3000))
    print(nearest_10000_multiple(6000))
    print(nearest_10000_multiple(8000))
    print(nearest_10000_multiple(22000))
    print(nearest_10000_multiple(28000))
