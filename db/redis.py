import json


key = "thumbnails"

class RedisThumbnail:
    def __init__(self, redis_db):
        self.redis_db = redis_db

    def save(self, thumb_dict):
        payload = json.dumps(thumb_dict)
        self.redis_db.rpush(key, payload)
        
