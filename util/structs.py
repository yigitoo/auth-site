from dataclasses import dataclass
from bson.objectid import ObjectId

@dataclass
class User:
    _id: ObjectId
    email: str
    username: str
    password: str
    id: str
    last_active: str
    is_active: bool
    

@dataclass
class BlogPost:
    title: str
    content: str
    _id: ObjectId
    title_with_id: str