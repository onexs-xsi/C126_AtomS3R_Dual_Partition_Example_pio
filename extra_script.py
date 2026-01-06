Import("env")
import os
import csv
import subprocess

# Get project directory
project_dir = env.get("PROJECT_DIR")
partitions_csv = os.path.join(project_dir, "partitions.csv")

# LittleFS configuration
LITTLEFS_BLOCK_SIZE = 4096

def parse_size(size_str):
    """Parse size string like '2M', '0x4000' to bytes"""
    size_str = size_str.strip()
    if size_str.endswith('M'):
        return int(size_str[:-1]) * 1024 * 1024
    elif size_str.endswith('K'):
        return int(size_str[:-1]) * 1024
    elif size_str.startswith('0x'):
        return int(size_str, 16)
    else:
        return int(size_str)

def get_partition_info(partition_name):
    """Get partition offset and size from partitions.csv"""
    offset = 0x9000  # Default start offset after bootloader

    with open(partitions_csv, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip comments and empty lines
            if not row or row[0].strip().startswith('#'):
                continue

            name = row[0].strip()
            ptype = row[1].strip() if len(row) > 1 else ''
            subtype = row[2].strip() if len(row) > 2 else ''
            part_offset = row[3].strip() if len(row) > 3 else ''
            size = row[4].strip() if len(row) > 4 else ''

            if not size:
                continue

            part_size = parse_size(size)

            # Use explicit offset if provided
            if part_offset:
                offset = parse_size(part_offset)

            if name == partition_name:
                return offset, part_size

            # Move to next partition
            offset += part_size

    return None, None

def build_littlefs_image(data_dir, image_path, size):
    """Build LittleFS image using mklittlefs"""
    # Get mklittlefs tool path
    platform = env.PioPlatform()
    tool_path = platform.get_package_dir("tool-mklittlefs")
    mklittlefs = os.path.join(tool_path, "mklittlefs")

    if os.name == 'nt':
        mklittlefs += ".exe"

    if not os.path.exists(mklittlefs):
        print(f"Error: mklittlefs not found at {mklittlefs}")
        return False

    # Calculate block count
    block_count = size // LITTLEFS_BLOCK_SIZE

    # Build command
    cmd = [
        mklittlefs,
        "-c", data_dir,
        "-b", str(LITTLEFS_BLOCK_SIZE),
        "-p", "256",  # page size
        "-s", str(size),
        image_path
    ]

    print(f"Building LittleFS image: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error building LittleFS image: {result.stderr}")
        return False

    print(f"LittleFS image created: {image_path}")
    return True

def upload_littlefs_image(image_path, offset):
    """Upload LittleFS image to device"""
    # Get esptool
    platform = env.PioPlatform()
    uploader = platform.get_package_dir("tool-esptoolpy")
    esptool = os.path.join(uploader, "esptool.py")

    # Get upload port - use subst for proper variable substitution
    upload_port = env.subst("$UPLOAD_PORT")
    if not upload_port:
        upload_port = "COM3"
    upload_speed = env.subst("$UPLOAD_SPEED")
    if not upload_speed:
        upload_speed = "460800"

    cmd = [
        env.subst("$PYTHONEXE") or "python",
        esptool,
        "--chip", "esp32s3",
        "--port", upload_port,
        "--baud", str(upload_speed),
        "write_flash",
        hex(offset),
        image_path
    ]

    print(f"Uploading LittleFS image: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    return result.returncode == 0

def uploadfs_a(source, target, env):
    """Upload LittleFS partition A"""
    data_dir = os.path.join(project_dir, "data_a")
    build_dir = env.subst("$BUILD_DIR")
    image_path = os.path.join(build_dir, "littlefs_a.bin")

    offset, size = get_partition_info("partitions_a")
    if offset is None:
        print("Error: partitions_a not found in partitions.csv")
        return

    print(f"Partition A: offset=0x{offset:x}, size={size}")

    if not os.path.exists(data_dir):
        print(f"Error: data directory not found: {data_dir}")
        return

    if build_littlefs_image(data_dir, image_path, size):
        upload_littlefs_image(image_path, offset)

def uploadfs_b(source, target, env):
    """Upload LittleFS partition B"""
    data_dir = os.path.join(project_dir, "data_b")
    build_dir = env.subst("$BUILD_DIR")
    image_path = os.path.join(build_dir, "littlefs_b.bin")

    offset, size = get_partition_info("partitions_b")
    if offset is None:
        print("Error: partitions_b not found in partitions.csv")
        return

    print(f"Partition B: offset=0x{offset:x}, size={size}")

    if not os.path.exists(data_dir):
        print(f"Error: data directory not found: {data_dir}")
        return

    if build_littlefs_image(data_dir, image_path, size):
        upload_littlefs_image(image_path, offset)

def uploadfs_all(source, target, env):
    """Upload all LittleFS partitions"""
    uploadfs_a(source, target, env)
    uploadfs_b(source, target, env)

def buildfs_a(source, target, env):
    """Build LittleFS image for partition A only"""
    data_dir = os.path.join(project_dir, "data_a")
    build_dir = env.subst("$BUILD_DIR")
    image_path = os.path.join(build_dir, "littlefs_a.bin")

    offset, size = get_partition_info("partitions_a")
    if offset is None:
        print("Error: partitions_a not found in partitions.csv")
        return

    print(f"Partition A: offset=0x{offset:x}, size={size}")

    if not os.path.exists(data_dir):
        print(f"Error: data directory not found: {data_dir}")
        return

    build_littlefs_image(data_dir, image_path, size)

def buildfs_b(source, target, env):
    """Build LittleFS image for partition B only"""
    data_dir = os.path.join(project_dir, "data_b")
    build_dir = env.subst("$BUILD_DIR")
    image_path = os.path.join(build_dir, "littlefs_b.bin")

    offset, size = get_partition_info("partitions_b")
    if offset is None:
        print("Error: partitions_b not found in partitions.csv")
        return

    print(f"Partition B: offset=0x{offset:x}, size={size}")

    if not os.path.exists(data_dir):
        print(f"Error: data directory not found: {data_dir}")
        return

    build_littlefs_image(data_dir, image_path, size)

def buildfs_all(source, target, env):
    """Build all LittleFS images"""
    buildfs_a(source, target, env)
    buildfs_b(source, target, env)

# Register custom targets
env.AddCustomTarget(
    name="uploadfs_a",
    dependencies=None,
    actions=[uploadfs_a],
    title="Upload LittleFS A",
    description="Build and upload LittleFS image for partition A"
)

env.AddCustomTarget(
    name="uploadfs_b",
    dependencies=None,
    actions=[uploadfs_b],
    title="Upload LittleFS B",
    description="Build and upload LittleFS image for partition B"
)

env.AddCustomTarget(
    name="uploadfs_all",
    dependencies=None,
    actions=[uploadfs_all],
    title="Upload All LittleFS",
    description="Build and upload all LittleFS images"
)

env.AddCustomTarget(
    name="buildfs_a",
    dependencies=None,
    actions=[buildfs_a],
    title="Build LittleFS A",
    description="Build LittleFS image for partition A"
)

env.AddCustomTarget(
    name="buildfs_b",
    dependencies=None,
    actions=[buildfs_b],
    title="Build LittleFS B",
    description="Build LittleFS image for partition B"
)

env.AddCustomTarget(
    name="buildfs_all",
    dependencies=None,
    actions=[buildfs_all],
    title="Build All LittleFS",
    description="Build all LittleFS images"
)
