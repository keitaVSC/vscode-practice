import requests
import os
from dotenv import load_dotenv

class NotionClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('NOTION_API_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_all_bookmarks(self):
        """Notionデータベースから全てのブックマークを取得"""
        endpoint = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        bookmarks = []
        try:
            response = requests.post(endpoint, headers=self.headers, json={
                "page_size": 100
            })
            if response.status_code == 200:
                results = response.json().get('results', [])
                for result in results:
                    try:
                        title = result['properties']['Title']['title'][0]['text']['content'] if result['properties']['Title']['title'] else 'Untitled'
                        url = result['properties']['URL']['url'] if 'url' in result['properties']['URL'] else ''
                        folder = result['properties'].get('Folder', {}).get('select', {}).get('name', '')
                        bookmarks.append({
                            'id': result['id'],
                            'title': title,
                            'url': url,
                            'folder': folder
                        })
                    except (KeyError, IndexError) as e:
                        print(f"Error processing bookmark: {e}")
                        continue
            return bookmarks
        except Exception as e:
            print(f"Error getting bookmarks: {e}")
            return []

    def bookmark_exists(self, url):
        """URLが既に存在するかチェック"""
        existing_bookmarks = self.get_all_bookmarks()
        return any(bookmark['url'].lower() == url.lower() for bookmark in existing_bookmarks)

    def add_bookmark(self, title, url, folder=None):
        """ブックマークを追加（重複チェック付き）"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"

            # 既に存在する場合はスキップ
            if self.bookmark_exists(url):
                print(f"Bookmark already exists: {title}")
                return True

            properties = {
                "Title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": title if title else "Untitled"
                            }
                        }
                    ]
                },
                "URL": {
                    "url": url
                }
            }

            if folder:
                properties["Folder"] = {
                    "select": {
                        "name": folder
                    }
                }

            endpoint = "https://api.notion.com/v1/pages"
            data = {
                "parent": {"database_id": self.database_id},
                "properties": properties
            }

            response = requests.post(endpoint, headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"Successfully added: {title} in folder: {folder}")
                return True
            else:
                print(f"Error adding {title}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error adding {title}: {str(e)}")
            return False

    def delete_bookmark(self, page_id):
        """ブックマークを削除"""
        try:
            endpoint = f"https://api.notion.com/v1/pages/{page_id}"
            response = requests.patch(endpoint, headers=self.headers, json={"archived": True})
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting bookmark: {e}")
            return False

    def update_existing_bookmarks(self, current_bookmarks):
        """現在のブックマークと比較して更新"""
        notion_bookmarks = self.get_all_bookmarks()
        current_urls = {bookmark.url.lower() for bookmark in current_bookmarks}
        deleted_count = 0

        # 不要なブックマークを削除
        for notion_bookmark in notion_bookmarks:
            bookmark_url = notion_bookmark['url'].lower()
            if bookmark_url and bookmark_url not in current_urls:
                if self.delete_bookmark(notion_bookmark['id']):
                    deleted_count += 1
                    print(f"Deleted bookmark: {notion_bookmark['title']}")

        return deleted_count