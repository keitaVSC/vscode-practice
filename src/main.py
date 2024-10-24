import logging
import os
from datetime import datetime
from notion_client import NotionClient
from chrome_client import ChromeClient

def setup_logging():
    # ログファイルをスクリプトと同じフォルダに作成
    log_path = os.path.join(os.path.dirname(__file__), 'bookmark_sync.log')
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_script_dir():
    """スクリプトのディレクトリパスを取得"""
    return os.path.dirname(os.path.abspath(__file__))

def main():
    try:
        # 実行場所に関係なくログを設定
        setup_logging()
        logging.info("Starting bookmark sync")
        logging.info(f"Script running from: {get_script_dir()}")
        
        chrome = ChromeClient()
        notion = NotionClient()

        # Chromeのブックマークを取得
        bookmarks = chrome.get_bookmarks()
        logging.info(f"Found {len(bookmarks)} bookmarks in Chrome")

        # 削除されたブックマークの処理
        deleted_count = notion.update_existing_bookmarks(bookmarks)
        logging.info(f"Deleted {deleted_count} bookmarks from Notion")

        # 新規追加・更新の処理
        updated_count = 0
        added_count = 0
        for bookmark in bookmarks:
            existing_bookmarks = notion.get_all_bookmarks()
            exists = any(existing['url'] == bookmark.url for existing in existing_bookmarks)
            
            if notion.add_bookmark(bookmark.title, bookmark.url, bookmark.folder):
                if exists:
                    updated_count += 1
                else:
                    added_count += 1

        completion_message = (
            f"Sync completed. "
            f"Added {added_count} new bookmarks, "
            f"Updated {updated_count} existing bookmarks, "
            f"Deleted {deleted_count} bookmarks."
        )
        logging.info(completion_message)
        print(completion_message)

    except Exception as e:
        error_message = f"Error during sync: {str(e)}"
        logging.error(error_message)
        print(error_message)

if __name__ == "__main__":
    main()