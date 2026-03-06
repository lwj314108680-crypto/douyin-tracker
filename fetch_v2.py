#!/usr/bin/env python3
"""
抖音监控 v2 - 支持历史时间序列
"""
import requests
import json
import sys
import time
import random
from datetime import datetime
from pathlib import Path

# 配置
API_URL = "https://dyvideo.app.padkeji.com/service/gql"
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data.json"
HISTORY_FILE = BASE_DIR / "history.json"

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36",
]

BASE_HEADERS = {
    "authorization": "L1VqU2dKUExEcnJweWE5VVhaa05WYjQ1YmtUR1FHc0I=",
    "cookie": "PHPSESSID=n7hfpc7ts1bdvf4eihvfi905gp",
    "content-type": "application/json"
}

def fetch_videos(page=1, retry=3):
    """获取视频列表"""
    query = {
        "query": f"""query{{
            userVideo{{
                search(page:{page}){{
                    list{{
                        id,
                        video{{
                            id,uid,authorName,title,publishAt,
                            videoStat,updateTime
                        }}
                    }},
                    pageInfo{{page,pageSize,total}}
                }}
            }}
        }}"""
    }
    
    headers = BASE_HEADERS.copy()
    headers["user-agent"] = random.choice(USER_AGENTS)
    
    for attempt in range(retry):
        try:
            resp = requests.post(API_URL, headers=headers, json=query, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < retry - 1:
                wait = random.uniform(5, 10)
                print(f"⚠️ 请求失败，{wait:.1f}秒后重试... ({attempt+1}/{retry})")
                time.sleep(wait)
            else:
                raise e

def load_history():
    """加载历史数据（时间序列）"""
    if not HISTORY_FILE.exists():
        return {}
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_history(history):
    """保存历史数据"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def process_data(current_videos):
    """处理数据：追加历史记录 + 计算增量"""
    history = load_history()
    now = int(time.time())
    today = datetime.now().strftime('%Y-%m-%d')
    
    processed = []
    
    for item in current_videos:
        v = item['video']
        video_id = v['videoStat']['aweme_id']
        current_play = int(v['videoStat']['play_count'])
        
        # 获取历史记录
        video_history = history.get(video_id, [])
        
        # 计算增量（与最近一次记录对比）
        if video_history:
            last_record = video_history[-1]
            delta = current_play - last_record['play_count']
        else:
            delta = 0
        
        # 追加新记录
        video_history.append({
            'play_count': current_play,
            'timestamp': now,
            'date': today
        })
        
        # 只保留最近7天
        video_history = [r for r in video_history if now - r['timestamp'] < 7*86400]
        history[video_id] = video_history
        
        processed.append({
            'id': video_id,
            'authorName': v['authorName'],
            'title': v['title'],
            'playCount': current_play,
            'delta': delta,
            'publishAt': v['publishAt'],
            'url': f"https://www.douyin.com/video/{video_id}"
        })
    
    # 按增量排序
    processed.sort(key=lambda x: x['delta'], reverse=True)
    
    # 保存历史
    save_history(history)
    
    return {
        'videos': processed,
        'updateTime': now * 1000
    }

def main():
    try:
        print("🚀 开始抓取数据...")
        
        # 抓取数据
        data = fetch_videos(page=1)
        videos = data['data']['userVideo']['search']['list']
        print(f"✅ 获取到 {len(videos)} 个视频")
        
        # 处理数据
        print("📊 计算增量...")
        result = process_data(videos)
        
        # 保存数据
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到 {DATA_FILE}")
        
        # 输出增长榜
        if result['videos']:
            print("\n🔥 增长榜 TOP 5:")
            for i, v in enumerate(result['videos'][:5], 1):
                print(f"{i}. @{v['authorName']} +{v['delta']:,}")
                print(f"   {v['title'][:40]}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
