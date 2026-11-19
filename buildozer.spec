[app]

# (str) Title of your application
title = KnightX_fsm

# (str) Package name
package.name = knightxfsm

# (str) Package domain (needed for android/ios packaging)
package.domain = org.knightx

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,db,json

# (list) Application requirements
requirements = python3,kivy,customtkinter,psutil,pycryptodomex,cryptography,bcrypt,pyjwt,requests

# (str) Presplash of the application
presplash.color = 0f172a

# (str) Icon of the application
icon.filename = assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, sensorPortrait, portrait, all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_FINE_LOCATION, CAMERA

# (int) Android API level to target
android.api = 33

# (int) Minimum API level
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version
android.ndk = 25b

# (bool) Copy libs instead of creating a libpymodules.so
android.copy_libs = 1

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.theme = Theme.AppCompat.NoActionBar

# (list) Source files to exclude
source.exclude_exts = spec

# (list) Source files to exclude (uncomment to use)
#source.exclude_patterns = license,images/*.png

# (str) Application version
version = 2.0.0

# (str) Application version code
version.code = 2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_root = 1

# (str) Path to buildozer working directory
build_dir = .buildozer

# (str) Output directory for the APK
output_dir = ./bin

# (str) Pattern to match for APK filename
#filename_pattern = %(app)s-%(version)s-%(code)s.apk

[android]

# (str) Android archive directory
android.arch = armeabi-v7a

# (str) Android services
android.services =

[android.local]

# (str) Android local recipes directory
android.local.recipes = .

# (str) Android local hooks directory
android.local.hooks = .

[android.with]

# (str) Python for Android (p4a) fork
p4a = master

[python]

# (str) Python version to use
python.version = 3.11

# (list) Python modules to include
python.modules = customtkinter, psutil, cryptography, bcrypt, pyjwt, requests

# (bool) Copy python modules to app
python.copy_modules = 1

[ios]

# (str) Python version for iOS
ios.python_version = 3.11

# (str) iOS deployment target
ios.deployment_target = 12.0

[accumulator]

# (str) Accumulator pattern
pattern = %(app)s-%(version)s.apk
