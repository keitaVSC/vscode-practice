import json
import os
from dataclasses import dataclass

@dataclass
class Bookmark:
    title: str
    url: str
    folder: str = None

class ChromeClient:
    def __init__(self):
        self.bookmarks_file = self._get_bookmarks_path()

    def _get_bookmarks_path(self):
        return os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks')

    def _parse_bookmarks(self, node, current_folder=None):
        bookmarks = []
        
        if node.get('type') == 'folder':
            current_folder = node.get('name')
            if 'children' in node:
                for child in node['children']:
                    bookmarks.extend(self._parse_bookmarks(child, current_folder))
        
        elif node.get('type') == 'url':
            bookmarks.append(Bookmark(
                title=node.get('name', ''),
                url=node.get('url', ''),
                folder=current_folder
            ))

        return bookmarks

    def get_bookmarks(self):
        try:
            with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                bookmarks = []
                
                # ブックマークバーとその他のブックマークの両方を処理
                for root in ['bookmark_bar', 'other']:
                    if root in data['roots']:
                        bookmarks.extend(self._parse_bookmarks(data['roots'][root]))
                
                return bookmarks
        except Exception as e:
            print(f"Error reading bookmarks: {e}")
            return []