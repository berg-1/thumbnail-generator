#! python3
# -*- coding:utf-8 -*-
# @Author  : berg-1
import argparse
import os.path
import re

from thumbnail.config import Config
from thumbnail.thumbnail import create_thumbnail


def create_thumbnails(video_path, config):
    vid_regex = r"\.(mov|mp4|m4v|mpg|mpeg|flv|wmv|avi|mkv|m2ts|ts)$"
    if os.path.isdir(video_path):
        print(f"{video_path} is folder")
        for _root, _dirs, _files in os.walk(video_path):
            for _file in _files:
                if not re.search(vid_regex, _file, re.IGNORECASE):
                    continue
                create_thumbnail(_root, _file, config)

    else:
        path, file = os.path.split(video_path)
        create_thumbnail(path, file, config)


def main():
    parser = argparse.ArgumentParser(description='This Python script generates video thumbnails with a customizable '
                                                 'grid layout and additional features like text overlays.')

    # Positional arguments
    parser.add_argument(
        "video",
        type=str,
        help="Path to the video file."
    )

    # Optional arguments
    parser.add_argument(
        "-r", "--rows",
        type=int,
        default=3,
        help="Number of images per row in the thumbnail grid (default: 3)."
    )
    parser.add_argument(
        "-c", "--cols",
        type=int,
        default=3,
        help="Number of images per column in the thumbnail grid (default: 3)."
    )
    parser.add_argument(
        "-b", "--bg-color",
        type=str,
        default="#2E2E2E",
        help="Background color of the thumbnail grid (default: #FFFFFF)."
    )
    parser.add_argument(
        "-f", "--text-font",
        type=str,
        default="arial.ttf",
        help="Path to the font file for text overlays (default: arial.ttf)."
    )
    parser.add_argument(
        "-ft", "--time-font",
        type=str,
        default="fonts/Georgia.ttf",
        help="Path to the font file for timestamp overlays (default: fonts/Georgia.ttf)."
    )
    parser.add_argument(
        "-c1", "--text-color",
        type=str,
        default="#FBFBFDFF",
        help="Font color for text overlays (default: #FBFBFDFF)."
    )
    parser.add_argument(
        "-c2", "--time-color",
        type=str,
        default="#FFFFFF99",
        help="Font color for timestamp overlays (default: #FFFFFF99)."
    )
    parser.add_argument(
        "-ol", "--outline",
        type=str,
        default="#00000040",
        help="Color for thumbnail outline (default: #00000040)."
    )
    parser.add_argument(
        "-s", "--shadow",
        type=str,
        default="#12121266",
        help="Back shadow color (default: #12121266)."
    )
    parser.add_argument(
        "-sb", "--shadow-bg",
        type=str,
        default="#2E2E2E",
        help="Back shadow background color (default: #2E2E2E)."
    )
    parser.add_argument(
        "-si", "--shadow-iter",
        type=int,
        default="10",
        help="Back shadow blur filter iter times (default: 10)."
    )
    parser.add_argument(
        "-m", "--output-mode",
        type=str,
        default="RGB",
        help="Output image mode: RGB for JPG, RGBA for PNG (default: RGB)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to save the generated thumbnail grid (default: filename)."
    )

    args = parser.parse_args()
    config = Config(args.output, rows=args.rows, cols=args.cols, bg_color=args.bg_color, font_text=args.text_font,
                    shadow=args.shadow, shadow_bg=args.shadow_bg, shadow_iter=args.shadow_iter,
                    font_timestamp=args.time_font, mode=args.output_mode)
    create_thumbnails(
        video_path=args.video,
        config=config
    )


if __name__ == "__main__":
    main()
