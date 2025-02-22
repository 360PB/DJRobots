# DJUU Music Downloader

一个用于下载 DJ呦呦音乐网 音乐的自动化工具。使用 Python 和 Selenium 实现，支持批量下载和自定义起始编号。

## 功能特点

- 🚀 自动批量下载音乐文件
- 📝 自动编号和重命名
- 🔄 断点续传支持
- 📊 下载进度显示
- 📋 详细的日志记录
- ⚙️ 可自定义 ChromeDriver 路径

## 系统要求

- Python 3.7+
- Google Chrome 浏览器
- Windows 系统（其他系统需要修改批处理文件）

## 安装说明

1. 克隆仓库到本地：
```bash
git clone https://github.com/yourusername/djuu-downloader.git
cd djuu-downloader
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
venv\Scripts\activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

4. 下载与你的 Chrome 浏览器版本匹配的 [ChromeDriver](https://sites.google.com/chromium.org/driver/)，并将其放在项目根目录。

## 使用方法

### 使用批处理文件运行（推荐）

直接运行 `start_download.bat`：
```bash
start_download.bat
```

带参数运行：
```bash
start_download.bat --start-page 1 --end-page 2 --start-index 1
```

### 直接运行 Python 脚本

基本用法：
```bash
python app.py
```

自定义参数：
```bash
python app.py --start-page 1 --end-page 2 --start-index 1
```

### 命令行参数说明

- `--start-page`: 起始页码（默认：1）
- `--end-page`: 结束页码（默认：100）
- `--start-index`: 文件编号起始值（默认：1）

## 项目结构

```
djuu-downloader/
├── app.py           # 主程序
├── start_download.bat  # 启动脚本
├── chromedriver.exe   # ChromeDriver (需自行下载)
├── requirements.txt   # 依赖包列表
├── downloads/         # 下载文件保存目录
└── download.log      # 下载日志文件
```

## 注意事项

1. 确保 ChromeDriver 版本与本地 Chrome 浏览器版本匹配
2. 下载的文件默认保存在 `downloads` 目录
3. 程序会自动跳过已下载的文件
4. 可以通过 `download.log` 查看详细的下载记录

## 故障排除

1. 如果出现 ChromeDriver 相关错误：
   - 检查 Chrome 浏览器版本
   - 下载对应版本的 ChromeDriver
   - 将 ChromeDriver 放在正确位置

2. 如果下载速度过慢：
   - 检查网络连接
   - 适当调整并发数量（在代码中修改 `max_workers` 参数）

3. 如果出现文件命名错误：
   - 检查保存路径是否包含非法字符
   - 确保有写入权限

## 开源协议

MIT License

## 免责声明

本工具仅用于学习和研究使用，请勿用于非法用途。使用本工具所产生的一切后果由使用者自行承担。
