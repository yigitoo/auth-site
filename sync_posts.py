from pymongo import MongoClient
from bson.objectid import ObjectId 
import os
from dotenv import load_dotenv as load_config
from dataclasses import dataclass
from uuid import uuid4 as generate_id

from util.structs import BlogPost

class SyncPosts(object):
    def __init__(self) -> None:
        load_config()
        self.DB_LINK = os.getenv('DB_LINK')
        
        self.post_datas: list[dict] = []
        self.sync()
        
        self.write_markdowns()

    def print(self):
        print(self.__str__())
    
    def __str__(self):
        self.result = ""
        self.newline = f'\n{"*" * 15}\n'
        for post in self.post_datas:
            self.result += '\n' + "---" * 5 + '\n'
            self.result += f'{self.newline.join(f"{key.capitalize()}: {value}" for key, value in post.items())}'
            self.result += '\n' + "---" * 5 + '\n'
        return self.result

    def sync(self) -> list[BlogPost]:
        client = MongoClient(self.DB_LINK)
        db = client['blog']
        self.post_datas = db.posts.find({})

    def write_markdowns(self):
        for post in self.post_datas:
            with open(f'./posts/{post["title_with_id"].lower().replace(" ", "-")}.md', 'w') as f:
                f.write(post["content"])

    def create_post(self, post_data: BlogPost) -> bool:
        random_id = str(generate_id())
        client = MongoClient(self.DB_LINK)
        db = client['blog']
        if not db.posts.find_one({
            "title": post_data['title']
        }):
            db.posts.insert_one({
                "_id": random_id,
                "title": post_data["title"],
                "content": post_data["content"],
                "title_with_id": f"{post_data['title'].lower().replace(' ', '-') + '-' + random_id}"
            })
            self.sync()
            self.write_markdowns()
            return True
        else:
            return False
if __name__ == "__main__":
    posts = SyncPosts()
    posts.create_post({
        "title": "HEBELE",
        "content": "Hello world"
    })
    posts.print()