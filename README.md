# ESP32-S3 双分区 LittleFS 示例 (PlatformIO)

本项目演示如何在 ESP32-S3 上使用**两个独立的 LittleFS 分区**存储文件。

## 项目结构

```
├── src/main.cpp          # 主程序
├── data_a/               # 分区 A 的文件（上传到 partitions_a）
├── data_b/               # 分区 B 的文件（上传到 partitions_b）
├── partitions.csv        # 分区表
├── platformio.ini        # PlatformIO 配置
└── extra_script.py       # 自定义上传脚本
```

## 分区布局

| 分区名 | 类型 | 大小 | 说明 |
|--------|------|------|------|
| nvs | data | 16KB | 非易失性存储 |
| phy_init | data | 4KB | PHY 初始化数据 |
| otadata | data | 8KB | OTA 数据 |
| factory | app | 3MB | 应用程序 |
| coredump | data | 64KB | 崩溃转储 |
| partitions_a | spiffs | 2MB | LittleFS 分区 A |
| partitions_b | spiffs | 2MB | LittleFS 分区 B |

---

## 快速开始

### 1. 编译并上传固件

```bash
pio run --target upload
```

### 2. 上传文件系统分区

**上传分区 A：**
```bash
pio run --target uploadfs_a
```

**上传分区 B：**
```bash
pio run --target uploadfs_b
```

**同时上传两个分区：**
```bash
pio run --target uploadfs_all
```

### 3. 查看串口输出

```bash
pio device monitor
```

---

## 如何维护项目

### 修改分区文件

1. **编辑 `data_a/` 中的文件** → 运行 `pio run --target uploadfs_a`
2. **编辑 `data_b/` 中的文件** → 运行 `pio run --target uploadfs_b`

> ⚠️ 修改文件后必须重新上传对应分区，否则设备上的文件不会更新！

### 添加新文件

直接在 `data_a/` 或 `data_b/` 文件夹中添加文件，然后上传对应分区即可。

### 修改代码

修改 `src/main.cpp` 后运行：
```bash
pio run --target upload
```

---

## 如何添加第三个分区 (data_c)

如果需要添加第三个分区 `partitions_c`，按以下步骤操作：

### 1. 修改 `partitions.csv`

添加一行：
```csv
partitions_c,   data, spiffs,  ,  2M,
```

### 2. 创建数据文件夹

创建 `data_c/` 文件夹，放入需要的文件。

### 3. 修改 `extra_script.py`

复制 `uploadfs_b` 和 `buildfs_b` 相关函数，改为 `uploadfs_c` 和 `buildfs_c`：
- 将 `data_b` 改为 `data_c`
- 将 `partitions_b` 改为 `partitions_c`
- 将 `littlefs_b.bin` 改为 `littlefs_c.bin`

并注册新的 target：
```python
env.AddCustomTarget(name="uploadfs_c", ...)
env.AddCustomTarget(name="buildfs_c", ...)
```

### 4. 修改 `src/main.cpp`

添加挂载和处理代码：
```cpp
if(mount_partition("partitions_c", "/part_c") == ESP_OK) {
    process_partition("/part_c");
}
```

### 5. 重新编译上传

```bash
pio run --target upload      # 上传固件
pio run --target uploadfs_c  # 上传分区 C
```

---

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 编译 | `pio run` |
| 上传固件 | `pio run --target upload` |
| 上传分区 A | `pio run --target uploadfs_a` |
| 上传分区 B | `pio run --target uploadfs_b` |
| 上传所有分区 | `pio run --target uploadfs_all` |
| 串口监视 | `pio device monitor` |
| 清理构建 | `pio run --target clean` |

---

## 注意事项

- 修改 `partitions.csv` 后需要重新上传**固件和所有分区**
- 分区类型虽然写的是 `spiffs`，但实际使用的是 LittleFS 文件系统
- 首次使用或分区表变更后，建议执行完整上传流程
