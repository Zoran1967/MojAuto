[app]
title = MojAuto
package.name = mojauto
package.domain = org.zoran

source.dir = .
source.include_exts = py,kv,txt,png,jpg
source.include_patterns = screens/*.py, kv/*.kv, database/*.py, database/__init__.py, screens/__init__.py, assets/*, assets/icons/*

icon.filename = %(source.dir)s/assets/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/assets/icon.png
icon.adaptive_background.filename = %(source.dir)s/assets/icon.png

version = 0.1

requirements = python3,kivy,camera4kivy,fpdf2,fonttools==4.28.0,plyer

orientation = portrait
fullscreen = 0

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a

android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
