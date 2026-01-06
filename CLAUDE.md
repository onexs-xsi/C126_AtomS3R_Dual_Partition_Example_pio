# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a dual-partition LittleFS example project for the M5Stack AtomS3R development board (ESP32-S3). The project demonstrates how to use two separate LittleFS filesystem partitions simultaneously.

The repository contains two implementations:
- **PlatformIO/Arduino version** (root directory) - Complete dual-partition implementation
- **ESP-IDF v5.5.1 version** (`example_idf551/`) - Reference implementation (uses SPIFFS)

## Build and Run Commands

### PlatformIO Commands

Use `platformio` or `pio` command (available in PATH after PlatformIO installation):

```bash
# Build the project
platformio run

# Upload firmware to device
platformio run --target upload

# Build LittleFS image for partition A
platformio run --target buildfs_a

# Build LittleFS image for partition B
platformio run --target buildfs_b

# Upload LittleFS partition A
platformio run --target uploadfs_a

# Upload LittleFS partition B
platformio run --target uploadfs_b

# Upload all LittleFS partitions
platformio run --target uploadfs_all

# Monitor serial output
platformio device monitor

# Clean build
platformio run --target clean
```

**Note**: If `platformio` command is not found, use the full path from PlatformIO installation:
- Windows: `%USERPROFILE%\.platformio\penv\Scripts\platformio.exe`
- Linux/macOS: `~/.platformio/penv/bin/platformio`

## Architecture

### Partition Layout (partitions.csv)
The project uses a custom partition table with two LittleFS data partitions:
- `nvs` - 16KB NVS partition
- `phy_init` - 4KB PHY init partition
- `otadata` - 8KB OTA data partition
- `factory` - 3MB app partition
- `coredump` - 64KB coredump partition
- `partitions_a` - 2MB LittleFS partition
- `partitions_b` - 2MB LittleFS partition

### Dual Partition Implementation

The main application (`src/main.cpp`) uses ESP32 native SPIFFS API:

1. **`mount_partition()`** - Mounts a SPIFFS partition using `esp_vfs_spiffs_register()`
2. **`process_partition()`** - Lists and processes all .txt files in a partition
3. **`read_txt_file()`** - Reads and displays text file contents
4. **`setup()`** - Initializes serial, mounts and processes both partitions

### Project Structure
```
.
├── src/
│   └── main.cpp           # Application entry point
├── data_a/                # Files embedded into partitions_a LittleFS image
│   ├── this_is_part_a_1.txt
│   ├── this_is_part_a_2.txt
│   └── this_is_part_a_3.txt
├── data_b/                # Files embedded into partitions_b LittleFS image
│   ├── this_is_part_b_1.txt
│   ├── this_is_part_b_2.txt
│   └── this_is_part_b_3.txt
├── partitions.csv         # Custom partition table definition
├── extra_script.py        # PlatformIO script for dual LittleFS support
├── platformio.ini         # PlatformIO configuration
└── example_idf551/        # ESP-IDF reference implementation
```

## Key Implementation Details

- **Target Board**: M5Stack AtomS3R (ESP32-S3)
- **Framework**: Arduino (via PlatformIO)
- **Flash Size**: 8MB
- **Filesystem**: LittleFS (more modern than SPIFFS)
- **Build System**: PlatformIO with custom extra_script.py

## Adding Files to Partitions

To add files to the LittleFS partitions:
1. Place files in `data_a/` directory for partitions_a
2. Place files in `data_b/` directory for partitions_b
3. Run `uploadfs_a`, `uploadfs_b`, or `uploadfs_all` target

## Custom Build Script (extra_script.py)

The `extra_script.py` provides custom targets for dual LittleFS support since PlatformIO only supports single filesystem partition by default:
- Parses `partitions.csv` to get partition offsets and sizes
- Uses `mklittlefs` tool to create LittleFS images from data directories
- Registers custom targets: `buildfs_a`, `buildfs_b`, `uploadfs_a`, `uploadfs_b`, `uploadfs_all`
