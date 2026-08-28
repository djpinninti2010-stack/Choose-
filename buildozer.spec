[app]
title = Cruise AI
package.name = cruiseai
package.domain = org.gopu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,google-genai,requests,speechrecognition,pyttsx3,opencv
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
