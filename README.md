# PodGPT

A simple command line tool to generate an infinitely streaming podcast using OpenAI's text generation and TTS models.

## Installation

1. Clone this repository
2. Create and activate a virtual environment with Python 3.11
    - Anaconda (*Recommended*): `conda create -n podgpt python=3.11` and `conda activate podgpt`
    - Virtualenv: `virtualenv -p python3.11 podgpt` and `source podgpt/bin/activate`
3. Install the requirements: `pip install -r requirements.txt`
4. Install [ffmpeg](https://ffmpeg.org/download.html)
    - Anaconda (*Recommended*): `conda install -c conda-forge ffmpeg`
    - Ubuntu: `sudo apt install ffmpeg`
    - Windows: [Download](https://ffmpeg.org/download.html) and add to PATH
    - MacOS (Homebrew): `brew install ffmpeg`
5. Rename `.env.example` to `.env` and fill in the values

## Usage

Run `python pod.py` and follow the prompts to generate a podcast. To stop the podcast, press `Ctrl+C`.
