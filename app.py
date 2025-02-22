import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import logging
from tqdm import tqdm
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 获取当前脚本所在目录
script_directory = os.path.dirname(os.path.abspath(__file__))
downloads_directory = os.path.join(script_directory, "downloads")

class WebDriver:
    """WebDriver 管理类"""
    @staticmethod
    def get_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # 从环境变量获取 ChromeDriver 路径
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
        if chromedriver_path and os.path.exists(chromedriver_path):
            return webdriver.Chrome(service=Service(chromedriver_path), options=options)
        else:
            # 如果环境变量未设置，使用默认方式
            from webdriver_manager.chrome import ChromeDriverManager
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def download_audio(url, save_path=None, index=None, downloaded_titles=None):
    """下载单个音频文件"""
    driver = None
    try:
        driver = WebDriver.get_driver()
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        # 使用显式等待获取元素
        audio_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//audio'))
        )
        audio_url = audio_element.get_attribute('src')

        title_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//h1'))
        )
        title = title_element.text.strip()

        if audio_url and title:
            logger.info(f"Found: {title}")

            # 检查标题是否已经下载过
            if downloaded_titles and title in downloaded_titles:
                logger.info(f"Duplicate title found: {title}")
                return
            downloaded_titles.add(title)

            # 确定保存路径
            sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            if index is not None:
                sanitized_title = f"{index:03d}_{sanitized_title}"
            save_path = save_path or os.path.join(downloads_directory, f"{sanitized_title}.m4a")

            # 检查文件是否已经存在
            if os.path.exists(save_path):
                logger.info(f"File exists: {save_path}")
                return

            # 下载音频文件，使用改进的进度条显示
            with requests.get(audio_url, stream=True, timeout=30) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                
                # 使用较短的文件名来避免进度条换行
                display_name = sanitized_title[:30] + "..." if len(sanitized_title) > 30 else sanitized_title
                
                with open(save_path, 'wb') as file, tqdm(
                    desc=display_name,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    ncols=100,  # 固定进度条宽度
                    bar_format='{desc:<35}{percentage:3.0f}%|{bar:30}{r_bar}'  # 自定义格式
                ) as pbar:
                    for data in response.iter_content(chunk_size=8192):
                        file.write(data)
                        pbar.update(len(data))

            logger.info(f"Downloaded: {save_path}")
            return True

    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return False
    finally:
        if driver:
            driver.quit()

def get_audio_play_links(url):
    """从主页中提取音频文件的播放地址和标题"""
    driver = None
    try:
        driver = WebDriver.get_driver()
        wait = WebDriverWait(driver, 10)
        driver.get(url)

        elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//table[@class='list_musiclist']//tr[position()>1]")
            )
        )

        play_links = []
        seen_links = set()

        for element in elements:
            try:
                link = element.find_element(By.XPATH, ".//a[@target='_Pt']")
                href = link.get_attribute('href')
                title = link.get_attribute('title')
                
                if href and title and href not in seen_links:
                    absolute_url = urljoin(url, href)
                    play_links.append((absolute_url, title))
                    seen_links.add(href)
            except Exception as e:
                logger.warning(f"Failed to extract link: {str(e)}")
                continue

        return play_links

    except Exception as e:
        logger.error(f"Error fetching links from {url}: {str(e)}")
        return []
    finally:
        if driver:
            driver.quit()

def batch_download_audios(play_links, start_index=1):
    """批量下载音频文件"""
    os.makedirs(downloads_directory, exist_ok=True)
    downloaded_titles = set()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for index, (link, title) in enumerate(play_links, start=start_index):
            save_path = os.path.join(
                downloads_directory,
                f"{index:03d}_{title.replace('/', '_').replace(':', '_')}.m4a"
            )
            future = executor.submit(
                download_audio,
                link,
                save_path,
                index,
                downloaded_titles
            )
            futures.append((future, title))
            # 添加小延迟以避免进度条重叠
            time.sleep(0.5)

        # 等待所有下载完成并处理异常
        for future, title in futures:
            try:
                result = future.result()
                if not result:
                    logger.error(f"Failed to download: {title}")
            except Exception as e:
                logger.error(f"Download failed for {title}: {str(e)}")

def main(start_page, end_page, start_index=1):
    """主函数，处理指定范围的页面"""
    base_url = "https://www.djuu.com/djlist/41_0_8_"
    
    total_downloads = 0
    failed_pages = []
    current_index = start_index

    for page in range(start_page, end_page + 1):
        try:
            page_url = f"{base_url}{page}.html"
            logger.info(f"Processing page {page}")
            
            play_links = get_audio_play_links(page_url)
            if play_links:
                logger.info(f"Found {len(play_links)} links on page {page}")
                batch_download_audios(play_links, current_index)
                total_downloads += len(play_links)
                current_index += len(play_links)
            else:
                logger.warning(f"No links found on page {page}")
                failed_pages.append(page)

        except Exception as e:
            logger.error(f"Error processing page {page}: {str(e)}")
            failed_pages.append(page)
            continue

    # 输出下载统计
    logger.info(f"Download completed. Total files: {total_downloads}")
    if failed_pages:
        logger.warning(f"Failed pages: {failed_pages}")

if __name__ == "__main__":
    os.chdir(script_directory)
    
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description='Download music from DJUU with custom start index.')
    parser.add_argument('--start-page', type=int, default=1, help='Start page number')
    parser.add_argument('--end-page', type=int, default=1, help='End page number')
    parser.add_argument('--start-index', type=int, default=1, help='Start index for file naming')
    
    args = parser.parse_args()
    
    try:
        main(args.start_page, args.end_page, args.start_index)
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"Program crashed: {str(e)}")
