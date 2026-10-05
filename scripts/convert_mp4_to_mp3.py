#!/usr/bin/env python3
"""Extract the first audio track from an MP4 file as an MP3."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def convert_mp4_to_mp3(input_path: Path, output_path: Path, bitrate: str) -> int:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        try:
            import imageio_ffmpeg

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            print(
                "FFmpeg was not found. Install project dependencies or install FFmpeg.",
                file=sys.stderr,
            )
            return 1

    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    if input_path.suffix.lower() != ".mp4":
        print(f"Input must be an MP4 file: {input_path}", file=sys.stderr)
        return 1

    if output_path.exists():
        print(f"Output already exists; not overwriting: {output_path}", file=sys.stderr)
        return 1

    command = [
        ffmpeg,
        "-hide_banner",
        "-i",
        str(input_path),
        "-map",
        "0:a:0",
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        bitrate,
        "-n",
        str(output_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        details = result.stderr.strip().splitlines()
        print("MP3 conversion failed:", file=sys.stderr)
        print("\n".join(details[-8:]), file=sys.stderr)
        return result.returncode

    print(f"Converted: {input_path} -> {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract audio from an MP4 file and save it as MP3."
    )
    parser.add_argument("input", type=Path, help="Path to the input MP4 file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output MP3 path (default: input filename with .mp3 extension)",
    )
    parser.add_argument(
        "-b",
        "--bitrate",
        default="192k",
        help="MP3 bitrate (default: 192k)",
    )
    args = parser.parse_args()

    output_path = args.output or args.input.with_suffix(".mp3")
    return convert_mp4_to_mp3(args.input, output_path, args.bitrate)


if __name__ == "__main__":
    raise SystemExit(main())