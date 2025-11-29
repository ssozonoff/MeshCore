from os.path import realpath

Import("env") # type: ignore
menv=env # type: ignore

src_filter = [
  '+<*.cpp>',
  '+<helpers/*.cpp>',
  '+<helpers/sensors>',
  '+<helpers/radiolib/*.cpp>',
  '+<helpers/ui/MomentaryButton.cpp>',
  '+<helpers/ui/buzzer.cpp>',
]

# add build and include dirs according to CPPDEFINES
for item in menv.get("CPPDEFINES", []):
 
    # PLATFORM HANDLING
    if item == "STM32_PLATFORM":
        src_filter.append("+<helpers/stm32/*>")
    elif item == "ESP32":
        src_filter.append("+<helpers/esp32/*>")
    elif item == "NRF52_PLATFORM":
        src_filter.append("+<helpers/nrf52/*>")
    elif item == "RP2040_PLATFORM":
        src_filter.append("+<helpers/rp2040/*>")
    
    # DISPLAY HANDLING
    elif isinstance(item, tuple) and item[0] == "DISPLAY_CLASS":
        display_class = item[1]
        src_filter.append(f"+<helpers/ui/{display_class}.cpp>")
        if (display_class == "ST7789Display") :
            src_filter.append(f"+<helpers/ui/OLEDDisplay.cpp>")
            src_filter.append(f"+<helpers/ui/OLEDDisplayFonts.cpp>")

    # VARIANTS HANDLING
    elif isinstance(item, tuple) and item[0] == "MC_VARIANT":
        variant_name = item[1]
        src_filter.append(f"+<../variants/{variant_name}>")
    
    # INCLUDE EXAMPLE CODE IN BUILD (to provide your own support files without touching the tree)
    elif isinstance(item, tuple) and item[0] == "BUILD_EXAMPLE":
        example_name = item[1]
        src_filter.append(f"+<../examples/{example_name}/*.cpp>")

    # EXCLUDE A SOURCE FILE FROM AN EXAMPLE (must be placed after example name or boom)
    elif isinstance(item, tuple) and item[0] == "EXCLUDE_FROM_EXAMPLE":
        exclude_name = item[1]
        if example_name is None:
            print("***** PLEASE DEFINE EXAMPLE FIRST *****")
            break
        src_filter.append(f"-<../examples/{example_name}/{exclude_name}>")

    # DEAL WITH UI VARIANT FOR AN EXAMPLE
    elif isinstance(item, tuple) and item[0] == "MC_UI_FLAVOR":
        ui_flavor = item[1]
        if example_name is None:
            print("***** PLEASE DEFINE EXAMPLE FIRST *****")
            break
        src_filter.append(f"+<../examples/{example_name}/{ui_flavor}/*.cpp>")
        
menv.Replace(SRC_FILTER=src_filter)

# Add ed25519 library to build
# This is needed when MeshCore is used as a dependency in other projects
import os
from os.path import join

# Get the library root directory
lib_root = menv.get("PROJECT_LIBDEPS_DIR")
if lib_root and "MeshCore" in str(lib_root):
    # When built as a dependency, find the MeshCore directory
    meshcore_dir = str(lib_root).rsplit("/libdeps/", 1)[0] + "/libdeps/" + str(lib_root).split("/libdeps/")[1].split("/")[0] + "/MeshCore"
else:
    # When built standalone (use relative path from this script)
    meshcore_dir = realpath(".")

ed25519_dir = join(meshcore_dir, "lib", "ed25519")
nrf52_include_dir = join(meshcore_dir, "lib", "nrf52", "include")

# Add ed25519 to include path
menv.Append(CPPPATH=[ed25519_dir])

# Add nrf52 includes if NRF52_PLATFORM is defined
for item in menv.get("CPPDEFINES", []):
    if item == "NRF52_PLATFORM":
        menv.Append(CPPPATH=[nrf52_include_dir])
        break

# Build ed25519 C files
if os.path.exists(ed25519_dir):
    menv.BuildSources(join("$BUILD_DIR", "ed25519"), ed25519_dir, src_filter="+<*.c>")

#print (menv.Dump())
