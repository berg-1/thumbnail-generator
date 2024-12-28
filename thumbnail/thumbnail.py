#! python3
# -*- coding:utf-8 -*-
# @Author  : berg-1
import base64
import os
import random
import string
import subprocess
import traceback

import av
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from .config import OutputFigure, nearest_10000_multiple, Config, TimePosition


def get_time_display(timestamp):
    """
    format timestamp
    """
    return "%02d:%02d:%02d" % (timestamp // 3600, timestamp % 3600 // 60, timestamp % 60)


def get_random_filename(ext):
    """
    generate random filename
    """
    return "".join([random.choice(string.ascii_lowercase) for _ in range(20)]) + ext


def str_to_base64(s):
    """encode str into base64"""
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


def base64_to_str(s):
    """decode base64 str"""
    return base64.b64decode(s.encode('utf-8')).decode('utf-8')


def get_file_size(res):
    """
    get file size
    """
    bu = 1024
    if res < bu:
        return f"{res}B"
    elif res < bu ** 2:
        return f"{res / bu:.2f}KB"
    elif res < bu ** 3:
        return f"{res / bu ** 2:.2f}MB"
    elif res < bu ** 4:
        return f"{res / bu ** 3:.2f}GB"
    else:
        return f"{res / bu ** 4:.2f}TB"


def make_shadow(width, height, color_mode, iterations=10, border=8, offset=(10, 10), background_color="#2E2E2E",
                shadow_color="#12121266"):
    """
    add image back shadow
    :param width: image width
    :param height: image height
    :param color_mode: color mode: RGB / RGBA
    :param iterations: blur filters
    :param border: shadow border width
    :param offset: shadow x and y offset
    :param background_color: bg color
    :param shadow_color: shadow color
    :return: image with back shadow
    """
    full_width = width + abs(offset[0]) + 2 * border
    full_height = height + abs(offset[1]) + 2 * border
    shadow = Image.new(color_mode, (full_width, full_height), background_color)

    shadow_left = border + max(offset[0], 0)  # if <0, push the rest of the image right
    shadow_top = border + max(offset[1], 0)  # if <0, push the rest of the image down
    shadow.paste(shadow_color, (shadow_left, shadow_top, shadow_left + width, shadow_top + height))
    # Apply the BLUR filter repeatedly
    for i in range(iterations):
        shadow = shadow.filter(ImageFilter.BLUR)
    # Paste the original image on top of the shadow
    img_left = 0
    img_top = 0
    if offset[0] < 0:
        img_left = border - min(offset[0], 0)  # if the shadow offset was <0, push right
    if offset[1] < 0:
        img_top = border - min(offset[1], 0)  # if the shadow offset was <0, push down
    # shadow.paste(image, (img_left, img_top))
    return shadow, (img_left, img_top)


def clac_time_position(time_pos: TimePosition, img_w, img_h, text_w, text_h, padding):
    """calculate timestamp coordination"""
    if time_pos == TimePosition.TOP_RIGHT:
        coords = (img_w - text_w - padding / 2, padding / 2)
    elif time_pos == TimePosition.CENTER:
        coords = ((img_w - text_w) / 2, (img_h - text_h) / 2)
    elif time_pos == TimePosition.BOTTOM_RIGHT:
        coords = (img_w - text_w - padding / 2, img_h - text_h - padding / 2)
    elif time_pos == TimePosition.TOP_LEFT:
        coords = (padding / 2, padding / 2)
    elif time_pos == TimePosition.BOTTOM_LEFT:
        coords = (padding / 2, img_h - text_h - padding / 2)
    else:
        raise ValueError(f"Invalid timestamp_position: {time_pos}")
    return coords


def get_frame_thumbnail(new_img: Image, timestamp: int, font: FreeTypeFont, shadow: Image, position: tuple[int, int],
                        fig: OutputFigure, time_position: TimePosition = TimePosition.TOP_RIGHT):
    """
    get frame thumbnail
    :param fig: configuration
    :param new_img: frame
    :param timestamp: timestamp
    :param time_position: position of timestamp
    :param font: font
    :param shadow: image shadow
    :param position: where the frame will be located
    :return: combined fame and shadow
    """
    new_img = new_img.convert("RGBA")
    text_overlay = Image.new("RGBA", new_img.size, (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(text_overlay)
    img_w, img_h = new_img.size
    # Calculate the width and height of the timestamp text
    time_display = get_time_display(timestamp)
    _, _, w, h = image_draw.textbbox((0, 0), time_display, font)

    # Calculate timestamp position
    coords = clac_time_position(time_position, img_w, img_h, w, h, fig.padding)
    # Draw the timestamp text at the specified position
    image_draw.text(coords, time_display,
                    fill=fig.color.timestamp, font=font, stroke_width=int(fig.fontSize / 16),
                    stroke_fill=fig.color.outline)  # 时间戳位置
    new_img = Image.alpha_composite(new_img, text_overlay)
    new_img = ImageOps.expand(new_img, border=fig.border, fill=(0, 0, 0, 100))
    shadow.paste(new_img, position)
    return shadow


def open_font(name, size):
    size = 10 if size <= 0 else size
    try:
        return ImageFont.truetype(font=name, size=size)
    except OSError:
        return ImageFont.truetype(font="arial.ttf", size=size)


def create_thumbnail(root_path, filename, config: Config):
    """
    generate the video thumbnails
    :param root_path: video root path
    :param filename: video file name
    :param config: configuration
    :return: None
    """
    print(f"processing: {filename}")
    if config.mode == "RGB":
        pic_name = f"{filename}.jpg"
    else:
        config.mode = "RGBA"
        pic_name = f"{filename}.png"
    if not config.output or not os.path.isdir(config.output):
        pic_path = os.path.join(root_path, pic_name)
    else:
        pic_path = os.path.join(config.output, pic_name)
    file_path = os.path.join(root_path, filename)
    prefix, ext = os.path.splitext(filename)
    random_filename = str_to_base64(prefix) + ext
    random_filename_2 = str_to_base64(prefix) + ext
    os.rename(file_path, os.path.join(root_path, random_filename))

    try:
        container = av.open(os.path.join(root_path, random_filename))
    except UnicodeDecodeError:
        print("metadata decode error. Try removing all the metadata...")
        subprocess.run(["ffmpeg", "-i", random_filename, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy",
                        random_filename_2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        container = av.open(os.path.join(root_path, random_filename_2))
    try:
        fig = OutputFigure(image_width=1024, image_height=1024, config=config)
        start = min(container.duration // (fig.cols * fig.rows), 5 * 1000000)
        end = container.duration - start
        time_marks = []
        for i in range(fig.rows * fig.cols):
            time_marks.append(start + (end - start) // (fig.rows * fig.cols - 1) * i)
        images = []
        for idx, mark in enumerate(time_marks):
            container.seek(mark)
            for frame in container.decode(video=0):
                images.append((frame.to_image(), mark // 1000000))
                break
        width, height = images[0][0].width, images[0][0].height
        frame_rate = container.streams.video[0].average_rate
        meta_vid = container.streams.video[0].codec_context
        meta_aud = container.streams.audio[0].codec_context
        bit_rate = container.bit_rate // 1024
        metadata = [f"Filename: {filename}",
                    f"Size: {get_file_size(container.size)} ({container.size:,} bytes)",
                    f"Resolution: {meta_vid.width}x{meta_vid.height}",
                    f"Duration: {get_time_display(container.duration // 1000000)}",
                    f"Video: {meta_vid.name.upper()} "
                    f"({container.streams.video[0].codec.long_name}) :: {bit_rate:,}kbps"
                    f", {float(frame_rate):.2f} fps",
                    f"Audio: {meta_aud.name.upper()} :: {meta_aud.sample_rate // 1000:,}kHz, "
                    f"{meta_aud.channels} channels, {len(container.streams.audio)} stream", ]
        enlarge_factor = nearest_10000_multiple(bit_rate)
        fig = OutputFigure(image_width=width * enlarge_factor, image_height=height * enlarge_factor, config=config)
        img = Image.new(config.mode, (fig.w, fig.w), fig.color.background)
        draw = ImageDraw.Draw(img)
        f1 = open_font(fig.font.font_text, fig.fontSize)
        f2 = open_font(fig.font.font_timestamp, fig.fontSize - 4)
        [_, top, _, bottom] = draw.textbbox(xy=(0, 0), text="\n".join(metadata), font=f1, spacing=fig.lineSpacing,
                                            stroke_width=int(fig.fontSize / 16))
        min_text_height = bottom - top + len(metadata) * fig.lineSpacing
        image_start_y = int(fig.padding * 1.6) + min_text_height
        img = Image.new(config.mode, (fig.w, image_start_y + fig.h), fig.color.background)
        draw = ImageDraw.Draw(img)
        draw.text((fig.padding, int(fig.padding * 0.8)), "\n".join(metadata), fig.color.text, f1,
                  spacing=fig.lineSpacing, stroke_fill=fig.color.outline, stroke_width=int(fig.fontSize / 16))
        shadow, position = make_shadow(fig.width, fig.height, config.mode, config.shadow_iter,
                                       fig.shadowBorder, fig.shadowOffset, fig.color.shadowBg,
                                       fig.color.shadow)  # generate shadow for reuse
        for idx, snippet in enumerate(images):
            y = idx // fig.cols
            x = idx % fig.cols
            new_img, timestamp = snippet
            new_img = new_img.resize((fig.width, fig.height), resample=Resampling.BILINEAR)
            x = fig.padding + (fig.padding + fig.width) * x
            y = image_start_y + (fig.padding + fig.height) * y
            img.paste(get_frame_thumbnail(new_img, timestamp, f2, shadow, position, fig, config.time_position),
                      box=(x, y))

        img.save(pic_path)

    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:
        container.close()
        os.rename(os.path.join(root_path, random_filename), file_path)
        if os.path.exists(random_filename_2):
            os.remove(os.path.join(root_path, random_filename_2))
            print(f"remove backup file {random_filename_2}")
