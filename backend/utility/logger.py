"""
自定義 Logger 配置
提供美化的日誌輸出格式，包含時間戳、彩色標籤和表情符號
"""

import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


class ColoredFormatter(logging.Formatter):
    """自定義彩色日誌格式化器"""
    
    # ANSI 顏色碼
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[34m',       # 藍色
        'WARNING': '\033[33m',    # 黃色/橘色
        'ERROR': '\033[31m',      # 紅色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m',       # 重置
        'BOLD': '\033[1m',        # 粗體
    }
    
    # 日誌等級表情符號和標籤
    LEVEL_ICONS = {
        'DEBUG': 'DEBUG',
        'INFO': 'INFO',
        'WARNING': 'WARNING',
        'ERROR': 'ERROR',
        'CRITICAL': 'CRITICAL',
    }
    
    def format(self, record):
        """格式化日誌記錄"""
        # 獲取當前時間 (hh:mm:ss.x 格式)
        now = datetime.now(ZoneInfo("Asia/Taipei"))
        timestamp = now.strftime('%H:%M:%S.%f')[:-5]  # 只保留一位毫秒
        
        # 獲取日誌等級
        levelname = record.levelname
        
        # 構建彩色的等級標籤
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        icon_label = self.LEVEL_ICONS.get(levelname, levelname)
        colored_level = f"{color}[{icon_label}]{self.COLORS['RESET']}"
        
        # 獲取日誌訊息
        message = record.getMessage()
        
        # 如果有異常資訊，添加到訊息後面
        if record.exc_info:
            if not message.endswith('\n'):
                message += '\n'
            message += self.formatException(record.exc_info)
        
        # 組合最終輸出: timestamp [LEVEL] message
        log_message = f"{timestamp} {colored_level} {message}"
        
        return log_message


def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    設置並返回一個配置好的 logger
    
    Args:
        name: logger 名稱，如果為 None 則使用 root logger
        level: 日誌等級 (預設為 INFO)
    
    Returns:
        配置好的 Logger 實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 創建控制台輸出 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 設置自定義格式化器
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)
    
    # 添加 handler 到 logger
    logger.addHandler(console_handler)
    
    # 防止日誌向上傳播到 root logger (避免重複輸出)
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    獲取或創建一個 logger
    
    Args:
        name: logger 名稱
    
    Returns:
        Logger 實例
    """
    return setup_logger(name)


# 預設的應用 logger
app_logger = setup_logger("mbbuddy")


if __name__ == "__main__":
    # 測試範例
    test_logger = setup_logger("test", logging.DEBUG)
    
    test_logger.debug("這是一條 DEBUG 訊息")
    test_logger.info("這是一條 INFO 訊息")
    test_logger.warning("這是一條 WARNING 訊息")
    test_logger.error("這是一條 ERROR 訊息")
    test_logger.critical("這是一條 CRITICAL 訊息")
    
    # 測試帶有表情符號的訊息
    test_logger.info("🚀 應用程式啟動中...")
    test_logger.info("✅ 連接成功")
    test_logger.warning("⚠️ 配置未找到，使用預設值")
    test_logger.error("❌ 連接失敗")