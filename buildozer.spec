[app]
title = Shoping
package.name = sopinglista
package.domain = org.teodora
source.dir = .
source.include_exts = py,kv,txt,png,jpg
source.include_patterns = screens/*.py, kv/*.kv, database/*.py, database/__init__.py, screens/__init__.py, assets/*, assets/icons/*
icon.filename = %(source.dir)s/assets/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/assets/icon_round.png
version = 0.1
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0

android.permissions =
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
