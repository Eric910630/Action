}(venv) root@iZ2zedh71ndzkct4ea2tynZ:~/Acticd /root/Action/backendtion/backend
source venv/bin/activate

# 执行种子数据脚本
python3 -m app.services.data.seed

# 验证创建结果
python3 << 'PYEOF'
from app.core.database import SessionLocal
from app.models.product import LiveRoom

db = SessionLocal()
try:
    rooms = db.query(LiveRoom).all()
    print(f"✅ 数据库中共有 {len(rooms)} 个直播间:")
    for room in rooms:
        print(f"  - {room.name} ({room.category})")
finally:
    db.close()
PYEOF

# 验证 API
echo -e "\n=== 验证 API ==="
curl http://localhost/api/v1/live-rooms/ | python3 -m json.tool
2025-11-15 23:42:51.693 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 时尚真惠选
2025-11-15 23:42:51.695 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 好物真惠选
2025-11-15 23:42:51.696 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 生活真惠选
2025-11-15 23:42:51.698 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 家居真惠选
2025-11-15 23:42:51.700 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 轻奢真惠选
2025-11-15 23:42:51.702 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 美妆真惠选
2025-11-15 23:42:51.704 | INFO     | __main__:create_initial_live_rooms:128 - 创建直播间: 童装真惠选
2025-11-15 23:42:51.712 | INFO     | __main__:create_initial_live_rooms:131 - 成功创建 7 个直播间，更新 0 个直播间
✅ 数据库中共有 7 个直播间:
  - 时尚真惠选 (女装)
  - 好物真惠选 (家具)
  - 生活真惠选 (家具)
  - 家居真惠选 (家电)
  - 轻奢真惠选 (奢侈品)
  - 美妆真惠选 (美妆)
  - 童装真惠选 (童装)

=== 验证 API ===
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2127  100  2127    0     0   412k      0 --:--:-- --:--:-- --:--:--  519k
{
    "items": [
        {
            "id": "4742a3e9-0c69-4e5e-9a68-1a206ba69c36",
            "name": "\u65f6\u5c1a\u771f\u60e0\u9009",
            "category": "\u5973\u88c5",
            "keywords": [
                "\u5973\u88c5",
                "\u65f6\u5c1a",
                "\u7a7f\u642d",
                "\u8fde\u8863\u88d9",
                "\u4e0a\u8863",
                "\u88e4\u5b50",
                "\u5916\u5957"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u65f6\u5c1a\u6f6e\u6d41",
            "created_at": "2025-11-15T23:42:51.693106",
            "updated_at": "2025-11-15T23:42:51.693110"
        },
        {
            "id": "a59c48ba-e21b-4298-960a-4944411a3b04",
            "name": "\u597d\u7269\u771f\u60e0\u9009",
            "category": "\u5bb6\u5177",
            "keywords": [
                "\u5bb6\u5177",
                "\u6c99\u53d1",
                "\u5e8a",
                "\u684c\u5b50",
                "\u6905\u5b50",
                "\u67dc\u5b50",
                "\u5bb6\u5c45"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u5b9e\u7528\u8010\u7528",
            "created_at": "2025-11-15T23:42:51.695058",
            "updated_at": "2025-11-15T23:42:51.695063"
        },
        {
            "id": "7055b9f5-db24-440f-9978-fb8cffcabf7d",
            "name": "\u751f\u6d3b\u771f\u60e0\u9009",
            "category": "\u5bb6\u5177",
            "keywords": [
                "\u5bb6\u5177",
                "\u8336\u51e0",
                "\u7535\u89c6\u67dc",
                "\u9910\u684c",
                "\u529e\u516c\u684c",
                "\u4e66\u67dc"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u73b0\u4ee3\u7b80\u7ea6",
            "created_at": "2025-11-15T23:42:51.696903",
            "updated_at": "2025-11-15T23:42:51.696907"
        },
        {
            "id": "ceae14b3-1b40-49ad-8357-0db8c8e3648f",
            "name": "\u5bb6\u5c45\u771f\u60e0\u9009",
            "category": "\u5bb6\u7535",
            "keywords": [
                "\u5bb6\u7535",
                "\u7535\u89c6",
                "\u51b0\u7bb1",
                "\u6d17\u8863\u673a",
                "\u7a7a\u8c03",
                "\u70ed\u6c34\u5668",
                "\u5c0f\u5bb6\u7535"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u79d1\u6280\u667a\u80fd",
            "created_at": "2025-11-15T23:42:51.698794",
            "updated_at": "2025-11-15T23:42:51.698798"
        },
        {
            "id": "6964a05f-4bcd-4cca-af56-7a8af407f87f",
            "name": "\u8f7b\u5962\u771f\u60e0\u9009",
            "category": "\u5962\u4f88\u54c1",
            "keywords": [
                "\u5962\u4f88\u54c1",
                "\u4e8c\u624b",
                "\u5305\u5305",
                "\u624b\u8868",
                "\u73e0\u5b9d",
                "\u540d\u724c",
                "\u5927\u724c"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u9ad8\u7aef\u7cbe\u81f4",
            "created_at": "2025-11-15T23:42:51.700856",
            "updated_at": "2025-11-15T23:42:51.700861"
        },
        {
            "id": "ce032818-2cc6-4188-a478-5517d1e8b80b",
            "name": "\u7f8e\u5986\u771f\u60e0\u9009",
            "category": "\u7f8e\u5986",
            "keywords": [
                "\u7f8e\u5986",
                "\u5316\u5986\u54c1",
                "\u62a4\u80a4\u54c1",
                "\u53e3\u7ea2",
                "\u7c89\u5e95",
                "\u773c\u5f71",
                "\u9762\u819c"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u7f8e\u4e3d\u65f6\u5c1a",
            "created_at": "2025-11-15T23:42:51.702758",
            "updated_at": "2025-11-15T23:42:51.702763"
        },
        {
            "id": "30a49e51-d21f-4b4d-bc7e-f8c77e6c54ed",
            "name": "\u7ae5\u88c5\u771f\u60e0\u9009",
            "category": "\u7ae5\u88c5",
            "keywords": [
                "\u7ae5\u88c5",
                "\u513f\u7ae5",
                "\u5b9d\u5b9d",
                "\u4eb2\u5b50",
                "\u7ae5\u978b",
                "\u7ae5\u5e3d"
            ],
            "ip_character": "\u7f57\u6c38\u6d69",
            "style": "\u6e29\u99a8\u53ef\u7231",
            "created_at": "2025-11-15T23:42:51.704662",
            "updated_at": "2025-11-15T23:42:51.704667"
        }
    ]
}
(venv) root@iZ2zedh71ndzkct4ea2tynZ:~/Action/backend# 