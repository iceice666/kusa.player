

> Because this author is still a student (yeah im 15),
> this project may not be updated very often.
> <br>
> Definitely not cause I'm lazy (ehe 🥲😂😅🥰😚

# Kusa

=======

A music player based on vlc-player.

## Features

- Supports lots of streaming platform[^1] and some video platform[^2] .
- Mouse-actionless, just only press some key on keyboard.
- Built-in search function, you can search for videos on Youtube or Bilibili without opening the browser.

## Before Use

Please install [vlc-player](https://wiki.videolan.org/Documentation:Installing_VLC/) first.

## Commands

[HERE](./cmd_help.md)

## THE FINAL GOAL (😅

I hope this project can be
**VERY BEAUTIFUL , VERY POWERFUL**[^3]

## TODOs

- [ ] Support Android
- [ ] Make a GUI

## Building

`For Windows`

```shell
powershell
pip install virtualenv
virtualenv .venv --python=3.10
./.venv/Scripts/activate.ps1
pip install -r ./requirements.txt
touch .venv/lib/site-packages/sitecustomize.py
```

`For Linux`

```shell
pip install virtualenv
virtualenv .venv --python=3.10
source .venv/bin/activate
pip install -r ./requiremrnt.txt
touch .venv/lib/site-packages/sitecustomize.py
```

[^1]:https://streamlink.github.io/plugins.html

[^2]: Basically, I only make sure that [Bilibili](https://www.bilibili.com/) and [Youtube](https://www.youtube.com/) these two websites can work, if the website that [streamlink plugins](https://streamlink.github.io/plugins.html) support, it might work tho.

[^3]: <https://www.tiktok.com/@spadaniel44/video/6873263608952818950>
