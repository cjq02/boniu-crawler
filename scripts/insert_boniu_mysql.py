import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pymysql


DB_CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "fuye_user"),
    password=os.getenv("DB_PASSWORD", "fuye345abc"),
    database=os.getenv("DB_NAME", "im_fuye"),
    charset=os.getenv("DB_CHARSET", "utf8mb4"),
    autocommit=True,
    cursorclass=pymysql.cursors.DictCursor,
)

TABLE_NAME = "ims_mdkeji_im_boniu_forum_post"


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    value = value.replace("/", "-")
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    return None


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def to_tiny(value: Any) -> int:
    if value in (True, 1, "1", "true", "True", "yes", "YES", "Y"):
        return 1
    return 0


def insert_posts(posts: List[Dict[str, Any]]) -> None:
    conn = pymysql.connect(**DB_CFG)
    sql = f"""
    INSERT INTO `{TABLE_NAME}` (
      `id`,`title`,`url`,`user_id`,`username`,`avatar_url`,
      `publish_time`,`reply_count`,`view_count`,`images`,`category`,
      `is_sticky`,`is_essence`,`crawl_time`,`type`,`is_crawl`
    ) VALUES (
      %s,%s,%s,%s,%s,%s,
      %s,%s,%s,%s,%s,
      %s,%s,%s,%s,%s
    )
    ON DUPLICATE KEY UPDATE
      `title`=VALUES(`title`),
      `url`=VALUES(`url`),
      `user_id`=VALUES(`user_id`),
      `username`=VALUES(`username`),
      `avatar_url`=VALUES(`avatar_url`),
      `publish_time`=VALUES(`publish_time`),
      `reply_count`=VALUES(`reply_count`),
      `view_count`=VALUES(`view_count`),
      `images`=VALUES(`images`),
      `category`=VALUES(`category`),
      `is_sticky`=VALUES(`is_sticky`),
      `is_essence`=VALUES(`is_essence`),
      `crawl_time`=VALUES(`crawl_time`),
      `type`=VALUES(`type`),
      `is_crawl`=VALUES(`is_crawl`);
    """
    try:
        with conn.cursor() as cur:
            rows = []
            for p in posts:
                images_json = json.dumps(p.get("images") or [], ensure_ascii=False)
                rows.append(
                    (
                        to_int(p.get("id") or 0),
                        (p.get("title") or "")[:255],
                        (p.get("url") or "")[:512],
                        (None if p.get("user_id") in (None, "") else to_int(p.get("user_id"))),
                        (p.get("username") or "")[:100],
                        (p.get("avatar_url") or None),
                        parse_datetime(p.get("publish_time")),
                        to_int(p.get("reply_count") or 0),
                        to_int(p.get("view_count") or 0),
                        images_json,
                        (p.get("category") or "")[:100],
                        to_tiny(p.get("is_sticky")),
                        to_tiny(p.get("is_essence")),
                        parse_datetime(p.get("crawl_time")),
                        (p.get("type") or "")[:50],
                        to_tiny(p.get("is_crawl", 1)),
                    )
                )
            if rows:
                cur.executemany(sql, rows)
    finally:
        conn.close()


def main():
    with open("data/boniu_forum_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)
    insert_posts(posts)
    print(f"Inserted/updated {len(posts)} rows into {TABLE_NAME}")


if __name__ == "__main__":
    main()


