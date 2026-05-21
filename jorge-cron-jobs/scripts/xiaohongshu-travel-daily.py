#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日小红书旅游攻略生成器
每晚23:00运行，随机选国内景点，生成小红书文案 + DALL-E 3海报提示词
发送邮件至 569545015@qq.com
发件人：权权养的虾（小红书）
"""

import random
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==================== 邮件配置 ====================
# 优先从 config.yaml 读取，否则使用默认值
try:
    from config_loader import get_mail_config
    _mail = get_mail_config()
    SMTP_SERVER = _mail.get('smtp_server', 'smtp.qq.com')
    SMTP_PORT = _mail.get('smtp_port', 465)
    SMTP_USER = _mail.get('smtp_user', '569545015@qq.com')
    SMTP_PASS = _mail.get('smtp_pass', '')
    TO_EMAIL = _mail.get('to_email', '569545015@qq.com')
except Exception:
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    SMTP_USER = "569545015@qq.com"
    SMTP_PASS = ""
    TO_EMAIL = "569545015@qq.com"

# ==================== 景点库 ====================
# 小众景点权重更高（weight），热门景点也有但概率低
DESTINATIONS = [
    # === 小众秘境 ===
    {"name": "沙溪古镇", "province": "云南", "days": 2, "type": "小众",
     "tags": ["茶马古道", "白族民居", "慢生活", "先锋书局"],
     "foods": ["土八碗", "地参子", "乳饼", "三道茶"],
     "highlight": "千年茶马古道上的幸存古镇，没有过度商业化"},
    {"name": "诺邓古村", "province": "云南", "days": 2, "type": "小众",
     "tags": ["千年白族村", "诺邓火腿", "盐井古道", "玉皇阁"],
     "foods": ["诺邓火腿", "井盐炒饭", "白族八大碗", "苦荞粑粑"],
     "highlight": "因《舌尖上的中国》诺邓火腿而出名的千年白族古村"},
    {"name": "普者黑", "province": "云南", "days": 3, "type": "小众",
     "tags": ["荷花海", "三生三世", "彝族村落", "喀斯特山水"],
     "foods": ["荷花宴", "荷叶炒蛋", "彝家腊肉", "醉虾"],
     "highlight": "万亩荷花盛放时的水上田园，彝族风情浓郁"},
    {"name": "东川红土地", "province": "云南", "days": 2, "type": "小众",
     "tags": ["上帝调色盘", "落霞沟", "锦绣园", "摄影天堂"],
     "foods": ["东川羊肉", "洋芋鸡", "荞粑粑", "包谷饭"],
     "highlight": "被上帝打翻调色盘的红土地，摄影师的天堂"},
    {"name": "肇兴侗寨", "province": "贵州", "days": 2, "type": "小众",
     "tags": ["鼓楼群", "侗族大歌", "梯田", "非遗"],
     "foods": ["酸汤鱼", "侗家腌鱼", "油茶", "糯米酒"],
     "highlight": "中国最大的侗族村寨，鼓楼群震撼人心"},
    {"name": "加榜梯田", "province": "贵州", "days": 2, "type": "小众",
     "tags": ["梯田云海", "苗族村落", "灌水季", "星空露营"],
     "foods": ["稻花鱼", "苗家酸汤", "五色糯米饭", "米酒"],
     "highlight": "可与元阳媲美的梯田，灌水季如天空之镜"},
    {"name": "荔波小七孔", "province": "贵州", "days": 2, "type": "小众",
     "tags": ["绿宝石", "水上森林", "68级瀑布", "鸳鸯湖"],
     "foods": ["荔波酸肉", "杨梅汤", "瑶族火塘饭", "烤香猪"],
     "highlight": "地球腰带上的绿宝石，水质清澈见底"},
    {"name": "色达", "province": "四川", "days": 3, "type": "小众",
     "tags": ["五明佛学院", "红房子", "天葬台", "藏传佛教"],
     "foods": ["糌粑", "酥油茶", "牦牛肉", "青稞酒"],
     "highlight": "漫山遍野的红房子，信仰的力量令人震撼"},
    {"name": "丹巴藏寨", "province": "四川", "days": 3, "type": "小众",
     "tags": ["甲居藏寨", "美人谷", "碉楼", "梨花"],
     "foods": ["藏式火锅", "牦牛肉干", "酥油糌粑", "酸奶"],
     "highlight": "中国最美乡村，梨花盛开时如童话世界"},
    {"name": "德天瀑布", "province": "广西", "days": 2, "type": "小众",
     "tags": ["跨国瀑布", "中越边境", "归春河", "竹筏"],
     "foods": ["越南春卷", "壮家五色饭", "百香果", "水历鱼"],
     "highlight": "亚洲第一跨国瀑布，中越边境的壮丽奇观"},
    {"name": "黄姚古镇", "province": "广西", "days": 2, "type": "小众",
     "tags": ["千年古镇", "带龙桥", "石板街", "豆豉"],
     "foods": ["黄姚豆豉", "豆腐酿", "南瓜花酿", "油茶"],
     "highlight": "养在深闺人未识的千年古镇，豆豉香飘千年"},
    {"name": "平潭岛", "province": "福建", "days": 3, "type": "小众",
     "tags": ["蓝眼泪", "风车田", "石头厝", "赶海"],
     "foods": ["时来运转", "八珍炒糕", "海蛎煎", "天长地久"],
     "highlight": "福建第一大岛，4-6月蓝眼泪大爆发"},
    {"name": "霞浦", "province": "福建", "days": 2, "type": "小众",
     "tags": ["滩涂光影", "紫菜养殖", "东壁日落", "摄影圣地"],
     "foods": ["霞浦海鲜", "闽南糊", "地瓜杯", "土笋冻"],
     "highlight": "中国最美滩涂，光影魔术师的天堂"},
    {"name": "南靖土楼", "province": "福建", "days": 2, "type": "小众",
     "tags": ["四菜一汤", "云水谣", "客家文化", "世界遗产"],
     "foods": ["客家酿豆腐", "土楼盐鸡", "梅菜扣肉", "米酒"],
     "highlight": "东方古堡，大鱼海棠的取景地"},
    {"name": "南浔古镇", "province": "浙江", "days": 2, "type": "小众",
     "tags": ["江南富庶", "小莲庄", "百间楼", "丝商故里"],
     "foods": ["双浇面", "浔蹄", "定胜糕", "橘红糕"],
     "highlight": "江南六大古镇中最富庶也最安静的一个"},
    {"name": "松阳", "province": "浙江", "days": 2, "type": "小众",
     "tags": ["最后的江南秘境", "杨家堂", "陈家铺", "民宿"],
     "foods": ["松阳薄饼", "沙擂", "灰汁糕", "糖糕"],
     "highlight": "被《中国国家地理》评为最后的江南秘境"},
    {"name": "东极岛", "province": "浙江", "days": 3, "type": "小众",
     "tags": ["中国第一缕阳光", "后会无期", "灯塔", "海钓"],
     "foods": ["海鲜面", "清蒸石斑", "海蜇皮", "东极螺酱"],
     "highlight": "中国第一缕阳光照射到的地方"},
    {"name": "花鸟岛", "province": "浙江", "days": 2, "type": "小众",
     "tags": ["蓝白小镇", "荧光海", "花鸟灯塔", "慢生活"],
     "foods": ["海鲜烧烤", "海石花", "贻贝", "鱼面"],
     "highlight": "中国的圣托里尼，蓝白房子配荧光海"},
    {"name": "篁岭", "province": "江西", "days": 2, "type": "小众",
     "tags": ["晒秋", "梯田花海", "悬崖古村", "徽派建筑"],
     "foods": ["婺源汽糕", "荷包红鲤鱼", "糊豆腐", "酒糟鱼"],
     "highlight": "挂在悬崖上的古村，秋天晒秋美如画"},
    {"name": "武功山", "province": "江西", "days": 2, "type": "小众",
     "tags": ["高山草甸", "云海日出", "徒步圣地", "帐篷节"],
     "foods": ["萍乡炒粉", "武功山烟笋", "莲花血鸭", "艾米果"],
     "highlight": "云中草原，户外徒步者的朝圣地"},
    {"name": "恩施大峡谷", "province": "湖北", "days": 3, "type": "小众",
     "tags": ["东方科罗拉多", "云龙地缝", "一炷香", "绝壁栈道"],
     "foods": ["恩施炕土豆", "土家合渣", "腊肉", "油茶汤"],
     "highlight": "媲美美国科罗拉多大峡谷的绝世奇观"},
    {"name": "神农架", "province": "湖北", "days": 3, "type": "小众",
     "tags": ["野人传说", "原始森林", "大九湖", "金丝猴"],
     "foods": ["神农架腊肉", "懒豆腐", "砣砣肉", "苞谷酒"],
     "highlight": "华中屋脊，北纬31°的绿色奇迹"},
    {"name": "扎尕那", "province": "甘肃", "days": 3, "type": "小众",
     "tags": ["石城", "藏寨", "仙女滩", "洛克之路"],
     "foods": ["藏包", "牦牛肉火锅", "酥油茶", "蕨麻猪"],
     "highlight": "被洛克誉为亚当夏娃的诞生地，石城秘境"},
    {"name": "禾木", "province": "新疆", "days": 3, "type": "小众",
     "tags": ["神的自留地", "图瓦人", "晨雾", "白桦林"],
     "foods": ["烤全羊", "手抓饭", "大盘鸡", "奶疙瘩"],
     "highlight": "神的自留地，秋天白桦林金黄一片"},
    {"name": "赛里木湖", "province": "新疆", "days": 2, "type": "小众",
     "tags": ["大西洋最后一滴眼泪", "环湖骑行", "野花", "雪山"],
     "foods": ["高白鲑", "手抓肉", "熏马肠", "哈萨克奶茶"],
     "highlight": "大西洋暖湿气流最后眷顾的地方"},
    {"name": "喀什古城", "province": "新疆", "days": 3, "type": "小众",
     "tags": ["丝路明珠", "艾提尕尔清真寺", "大巴扎", "维吾尔风情"],
     "foods": ["烤包子", "抓饭", "馕坑肉", "酸奶粽子"],
     "highlight": "活着的千年古城，不到喀什不算到新疆"},
    {"name": "林芝", "province": "西藏", "days": 3, "type": "小众",
     "tags": ["桃花沟", "南迦巴瓦", "雅鲁藏布", "西藏江南"],
     "foods": ["石锅鸡", "藏香猪", "酥油茶", "牦牛肉"],
     "highlight": "西藏江南，3月桃花盛开时美如仙境"},
    {"name": "额济纳", "province": "内蒙古", "days": 3, "type": "小众",
     "tags": ["胡杨林", "黑城", "怪树林", "戈壁"],
     "foods": ["手扒肉", "奶酪", "驼肉馅饼", "蒙古奶茶"],
     "highlight": "三千年不死、不倒、不朽的胡杨林"},
    {"name": "阿尔山", "province": "内蒙古", "days": 3, "type": "小众",
     "tags": ["天池", "杜鹃湖", "火山地貌", "森林公园"],
     "foods": ["铁锅炖", "烤羊腿", "蒙古锅茶", "山野菜"],
     "highlight": "中国的瑞士，火山与森林的完美结合"},
    {"name": "漠河北极村", "province": "黑龙江", "days": 3, "type": "小众",
     "tags": ["中国最北", "极光", "白桦林", "冰雪世界"],
     "foods": ["铁锅炖大鹅", "杀猪菜", "冻梨", "粘豆包"],
     "highlight": "找北之旅，中国最北端的童话雪国"},
    {"name": "雪乡", "province": "黑龙江", "days": 2, "type": "小众",
     "tags": ["蘑菇屋", "童话世界", "雪地徒步", "东北火炕"],
     "foods": ["锅包肉", "小鸡炖蘑菇", "冻柿子", "糖葫芦"],
     "highlight": "现实版的童话雪国，蘑菇屋顶美到犯规"},
    {"name": "长白山", "province": "吉林", "days": 3, "type": "小众",
     "tags": ["天池", "温泉", "林海雪原", "朝鲜族风情"],
     "foods": ["朝鲜冷面", "石锅拌饭", "烤肉", "人参鸡汤"],
     "highlight": "东北第一神山，天池云雾缭绕如仙境"},

    # === 热门但经典 ===
    {"name": "大理洱海", "province": "云南", "days": 3, "type": "热门",
     "tags": ["风花雪月", "苍山洱海", "白族", "慢生活"],
     "foods": ["白族酸辣鱼", "乳扇", "饵丝", "三道茶"],
     "highlight": "风花雪月的浪漫，去有风的地方"},
    {"name": "丽江古城", "province": "云南", "days": 3, "type": "热门",
     "tags": ["纳西文化", "玉龙雪山", "束河古镇", "酒吧街"],
     "foods": ["腊排骨火锅", "鸡豆凉粉", "纳西烤鱼", "黑山羊"],
     "highlight": "艳遇之都，玉龙雪山下的千年古城"},
    {"name": "九寨沟", "province": "四川", "days": 3, "type": "热门",
     "tags": ["人间仙境", "五彩池", "诺日朗瀑布", "原始森林"],
     "foods": ["牦牛肉", "青稞酒", "酥油茶", "洋芋糍粑"],
     "highlight": "九寨归来不看水，人间瑶池"},
    {"name": "张家界", "province": "湖南", "days": 3, "type": "热门",
     "tags": ["阿凡达取景地", "天门山", "玻璃栈道", "武陵源"],
     "foods": ["三下锅", "葛根粉", "土家腊肉", "酸肉"],
     "highlight": "潘多拉星球的灵感来源，奇峰三千"},
    {"name": "桂林阳朔", "province": "广西", "days": 3, "type": "热门",
     "tags": ["山水甲天下", "漓江竹筏", "西街", "喀斯特"],
     "foods": ["桂林米粉", "啤酒鱼", "田螺酿", "荔浦芋扣肉"],
     "highlight": "山水甲天下，二十元人民币背景"},
    {"name": "西安", "province": "陕西", "days": 3, "type": "热门",
     "tags": ["十三朝古都", "兵马俑", "回民街", "大唐不夜城"],
     "foods": ["肉夹馍", "凉皮", "羊肉泡馍", "biangbiang面"],
     "highlight": "千年古都，碳水天堂"},
    {"name": "敦煌", "province": "甘肃", "days": 3, "type": "热门",
     "tags": ["莫高窟", "鸣沙山月牙泉", "丝路", "阳关"],
     "foods": ["驴肉黄面", "杏皮水", "胡杨焖饼", "羊肉粉汤"],
     "highlight": "大漠孤烟直，千年丝路明珠"},
    {"name": "三亚", "province": "海南", "days": 4, "type": "热门",
     "tags": ["椰林海滩", "蜈支洲岛", "免税城", "热带风情"],
     "foods": ["文昌鸡", "和乐蟹", "抱罗粉", "清补凉"],
     "highlight": "东方夏威夷，椰风海韵"},
]

# ==================== 文艺标题模板 ====================
TITLE_TEMPLATES = [
    "{name}的风，把心事吹成了诗",
    "我在{name}，等一场{season}的约会",
    "去{name}吧，那里藏着{adj}的梦",
    "{name}：{time}最该去的地方",
    "藏在{province}的{name}，{adj}得让人心颤",
    "{name}不只有{tag}，还有{adj}的{thing}",
    "被{name}治愈了，{time}一定要去",
    "{name}｜{adj}到窒息的{thing}",
    "{adj}预警！{name}的{thing}美到犯规",
    "{name}日记：{time}的{adj}慢生活",
    "不是{place}去不起，而是{name}更有性价比",
    "{name}，一个{adj}到让人忘记时间的地方",
    "去{name}做一场{adj}的梦｜{time}旅行指南",
    "{name}：当{tag}遇上{adj}的{thing}",
    "{adj}爆表！{name}这个{thing}谁懂啊",
]

SEASON_WORDS = ["春日", "盛夏", "金秋", "深冬", "四季", "这个秋天", "这个夏天"]
ADJ_WORDS = ["浪漫", "治愈", "绝美", "惊艳", "梦幻", "温柔", "慵懒", "诗意",
              "静谧", "震撼", "小众", "宝藏", "神仙", "绝绝子", "氛围感"]
THING_WORDS = ["日落", "晨雾", "星空", "晚霞", "云海", "花海", "古镇", "梯田",
               "山水", "夜景", "烟火气", "慢时光", "秘境", "童话"]
PLACE_WORDS = ["瑞士", "日本", "新西兰", "冰岛", "托斯卡纳"]

# ==================== 话题标签 ====================
HASHTAG_POOL = [
    "#旅行", "#旅游攻略", "#小众旅行地", "#国内旅游日常", "#治愈系风景",
    "#美食", "#旅途中的美景", "#周末去哪儿", "#假期去哪玩", "#特种兵旅游",
    "#一个人的旅行", "#穷游", "#大学生旅游", "#打工人旅游", "#带娃旅行",
    "#蜜月旅行", "#摄影", "#氛围感", "#拍出氛围感", "#旅行穿搭",
    "#酒店", "#民宿", "#露营", "#徒步", "#自驾游",
    "#古镇", "#海岛", "#山水", "#人文景点分享", "#非遗",
    "#小红书旅行月历", "#旅行梦想家", "#我的旅行日记", "#旅行随手拍", "#旅行推荐官",
]


def get_season():
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "春天"
    elif month in [6, 7, 8]:
        return "夏天"
    elif month in [9, 10, 11]:
        return "秋天"
    else:
        return "冬天"


def generate_title(dest):
    """生成文艺标题"""
    template = random.choice(TITLE_TEMPLATES)
    season = get_season()
    adj = random.choice(ADJ_WORDS)
    thing = random.choice(THING_WORDS)
    place = random.choice(PLACE_WORDS)
    tag = random.choice(dest["tags"]) if dest["tags"] else "风景"

    # 根据模板填充
    title = template.format(
        name=dest["name"],
        province=dest["province"],
        season=season,
        time=random.choice(SEASON_WORDS),
        adj=adj,
        thing=thing,
        place=place,
        tag=tag
    )
    return title


def generate_itinerary(dest):
    """生成行程规划"""
    days = dest["days"]
    foods = dest["foods"]
    tags = dest["tags"]
    name = dest["name"]
    province = dest["province"]

    # 根据天数生成行程
    if days == 1:
        itinerary = f"""Day 1｜{name}精华一日游
- 上午：抵达{name}，{random.choice(tags)}打卡，感受{random.choice(['晨曦', '晨光', '第一缕阳光'])}
- 午餐：必吃{foods[0]}，{random.choice(['当地老字号', '网红小店', '街边苍蝇馆子'])}最正宗
- 下午：深入{random.choice(tags)}，{random.choice(['拍照出片', '发呆放空', '慢慢逛'])}
- 晚餐：{foods[1]}，{random.choice(['配当地米酒', '配特色蘸料', '老板推荐的隐藏菜单'])}
- 晚上：{random.choice(['看星空', '逛夜市', '找家小酒馆', '民宿露台吹风'])}"""
    elif days == 2:
        itinerary = f"""Day 1｜初见{name}
- 上午：抵达{name}，入住{random.choice(['景观民宿', '古镇客栈', '当地特色酒店'])}
- 午餐：{foods[0]}，{random.choice(['舌尖上的非遗', '当地人从小吃到大的味道', '老板祖传秘方'])}
- 下午：{random.choice(tags)}漫步，{random.choice(['拍大片', '寻找最佳机位', '和当地人聊天'])}
- 晚餐：{foods[1]}，{random.choice(['配自酿米酒', '边吃边听民谣', '露天烧烤氛围感'])}
- 晚上：{random.choice(['露台看星空', '古镇夜游', '民宿小院喝茶'])}

Day 2｜深度{name}
- 早起：{random.choice(['看日出', '逛早市', '晨雾中的'+name])}
- 早餐：{random.choice(['当地特色早餐', '街边热气腾腾的小吃', '民宿老板的手作早餐'])}
- 上午：打卡{random.choice(tags)}，{random.choice(['避开人群的小众机位', '本地人才知道的秘密地点'])}
- 午餐：{foods[2]}，{random.choice(['苍蝇馆子才有灵魂', '老店不需要招牌', '一碗入魂'])}
- 下午：{random.choice(['买伴手礼', '再找一家咖啡馆发呆', '最后再看一眼'+name])}
- 返程前：{random.choice(['带一份'+foods[0]+'路上吃', '和老板道别', '写一张明信片'])}
"""
    else:  # 3天及以上
        itinerary = f"""Day 1｜初识{name}
- 上午：抵达{name}，入住{random.choice(['核心区域民宿', '景区门口客栈', '当地人家'])}
- 午餐：{foods[0]}，{random.choice(['第一顿就封神', '盲点都不踩雷'])}
- 下午：打卡{random.choice(tags)}，{random.choice(['暴走模式开启', '随手拍都是壁纸'])}
- 晚餐：{foods[1]}，{random.choice(['配冰镇啤酒', '配自酿果酒', '配一壶热茶'])}
- 晚上：{random.choice(['夜游古镇', '看夜景', '民宿露台看星星'])}

Day 2｜深入{name}
- 早起：{random.choice(['日出前的静谧', '晨雾缭绕中的'+name])}
- 早餐：{random.choice(['当地传统早餐', '民宿老板亲自下厨', '街边百年老店'])}
- 上午：{random.choice(tags)}深度游，{random.choice(['徒步探索', '租辆电动车环湖', '坐当地人的摩的'])}
- 午餐：{foods[2]}，{random.choice(['山里的农家乐', '水边的鱼庄', '巷子深处的小馆'])}
- 下午：{random.choice(['小众机位拍照', '和当地人学做手工艺品', '找个茶馆发呆'])}
- 晚餐：{foods[3]}，{random.choice(['夜市大排档', '河边的烛光晚餐', '老板推荐的私房菜'])}
- 晚上：{random.choice(['逛夜市淘好物', '听当地老人讲故事', '酒吧听民谣'])}

Day 3｜告别{name}
- 早起：{random.choice(['最后的日出', '再去一次最爱的角落', '晨跑/'+name])}
- 早餐：{random.choice(['把所有喜欢的再吃一遍', '解锁最后一家早餐店'])}
- 上午：{random.choice(['买伴手礼', '写明信片', '最后再拍一组照片'])}
- 午餐：{random.choice([foods[0]+'打包带走', '最后一顿大餐', '老板的隐藏菜单'])}
- 下午：{random.choice(['带着不舍离开', '计划下次再来', '已经在想下一次了'])}
"""
    return itinerary


def generate_hashtags(dest):
    """生成至少6个话题标签"""
    base_tags = [
        f"#{dest['name']}",
        f"#{dest['province']}旅游",
        f"#{dest['name']}攻略",
    ]

    # 随机选3-5个通用标签
    common_tags = random.sample(HASHTAG_POOL, random.randint(3, 5))

    # 根据类型加标签
    if dest["type"] == "小众":
        type_tags = ["#小众旅行地", "#宝藏旅游地", "#人少景美"]
    else:
        type_tags = ["#国内旅游", "#必打卡", "#经典路线"]

    # 随机选1-2个类型标签
    selected_type = random.sample(type_tags, random.randint(1, 2))

    all_tags = base_tags + common_tags + selected_type
    # 打乱顺序
    random.shuffle(all_tags)
    return " ".join(all_tags)


def generate_dalle_prompt(dest):
    """生成DALL-E 3海报提示词"""
    name = dest["name"]
    province = dest["province"]
    tags = dest["tags"]
    highlight = dest["highlight"]

    # 根据景点特征构建描述
    scene_descriptions = {
        "古镇": f"ancient town with traditional architecture, stone-paved streets, old wooden houses, red lanterns hanging, morning mist rising from the river",
        "梯田": f"spectacular terraced fields cascading down mountainsides, water-filled paddies reflecting sky, morning mist between layers",
        "瀑布": f"magnificent waterfall plunging from cliffs, rainbow in the mist, lush tropical vegetation surrounding",
        "海岛": f"tropical island paradise, crystal clear turquoise water, white sandy beach, palm trees swaying, wooden fishing boats",
        "雪山": f"snow-capped mountain peak piercing through clouds, alpine meadows below, prayer flags fluttering in wind",
        "湖泊": f"pristine alpine lake with mirror-like surface, snow-capped mountains reflected perfectly, wildflowers on shore",
        "沙漠": f"vast golden desert dunes stretching to horizon, camel caravan silhouette, dramatic sunset sky",
        "森林": f"dense primeval forest with towering ancient trees, sunlight filtering through canopy, moss-covered ground",
        "峡谷": f"dramatic canyon with sheer cliff walls, turquoise river running through bottom, mist rising from depths",
    }

    # 匹配场景类型
    scene_type = "landscape"
    for key, desc in scene_descriptions.items():
        if any(key in tag for tag in tags) or key in name:
            scene_type = desc
            break

    if scene_type == "landscape":
        # 默认景观描述
        scene_type = f"breathtaking natural landscape of {name}, iconic scenery with dramatic lighting, {random.choice(tags)} as focal point"

    prompt = f"""A stunning first-person perspective travel poster of {name} in {province}, China. The viewer stands at the perfect viewpoint looking out at the {scene_type}. Golden hour lighting bathes everything in warm, dreamy glow. The composition is cinematic and magazine-quality, with rich colors and ultra-detailed textures. {highlight}. Travel poster style with artistic Chinese aesthetic, atmospheric and evocative, 8K quality, professional travel photography composition, warm and inviting mood. Minimal clean space at top for text overlay."""

    return prompt


def generate_xiaohongshu_content(dest):
    """生成完整小红书内容"""
    title = generate_title(dest)
    itinerary = generate_itinerary(dest)
    hashtags = generate_hashtags(dest)

    # 行程天数文字
    days_text = f"{dest['days']}天{dest['days']-1}夜" if dest['days'] > 1 else "1日游"

    # 正文开头
    intros = [
        f"刚从{dest['name']}回来，整个人都被治愈了😭",
        f"去{dest['name']}是我今年最正确的决定！",
        f"{dest['name']}真的{random.choice(ADJ_WORDS)}到我了，必须安利给你们！",
        f"答应我，{get_season()}一定要去一次{dest['name']}！",
        f"{dest['name']}｜一个让我想原地退休的地方",
    ]

    # Tips
    tips = [
        f"✅ 最佳游玩时间：{random.choice(['春秋两季', get_season(), '避开节假日', '清晨和傍晚'])}，光线最美",
        f"✅ {random.choice(['防晒！紫外线很强', '带好充电宝，美景太多手机耗电快', '穿舒适的鞋，暴走警告', '提前订住宿，旺季一房难求'])}",
        f"✅ {random.choice(['当地特产'+dest['foods'][0]+'可以带走', '记得砍价，对半砍', '和老板聊聊天，能获得隐藏玩法', '早起！避开人流高峰'])}",
        f"✅ {random.choice(['交通建议：'+random.choice(['自驾最方便', '高铁+当地包车', '飞机转大巴', '建议报当地小团']), '穿搭建议：'+random.choice(['浅色衣服出片', '民族风穿搭很搭', '带件外套早晚温差大']), '美食提醒：'+random.choice([dest['foods'][0]+'必吃', '苍蝇馆子比网红店好吃', '晚上别错过夜市'])])}",
    ]

    # 结尾
    endings = [
        "这里不大，但足够你发呆一整天。趁还没大火，赶紧去！",
        "人生建议：去这里，就现在。",
        "真心推荐：去这里，趁年轻。",
    ]
    # 替换占位符
    endings = [e.replace("这里", dest['name']) for e in endings]

    content = f"""{random.choice(intros)}

📍 {dest['province']} · {dest['name']} · {days_text}攻略

{itinerary}

💡 Tips：
{chr(10).join(random.sample(tips, min(3, len(tips))))}

{random.choice(endings)}

{hashtags}
"""

    return title, content


def generate_email_html(dest, title, content, dalle_prompt):
    """生成邮件HTML"""
    today = datetime.now().strftime("%Y年%m月%d日")
    days_text = f"{dest['days']}天{dest['days']-1}夜" if dest['days'] > 1 else "1日游"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fafafa; margin: 0; padding: 20px; }}
.container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
.header {{ background: linear-gradient(135deg, #ff2442 0%, #ff6b6b 100%); padding: 30px; text-align: center; }}
.header h1 {{ color: white; margin: 0; font-size: 24px; }}
.header .date {{ color: rgba(255,255,255,0.8); margin-top: 8px; font-size: 14px; }}
.section {{ padding: 24px 30px; border-bottom: 1px solid #f0f0f0; }}
.section:last-child {{ border-bottom: none; }}
.section-title {{ font-size: 18px; font-weight: 700; color: #333; margin-bottom: 16px; display: flex; align-items: center; }}
.section-title .icon {{ margin-right: 8px; font-size: 20px; }}
.content-text {{ font-size: 15px; line-height: 1.8; color: #444; white-space: pre-line; }}
.prompt-box {{ background: #f8f9fa; border-radius: 12px; padding: 20px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.7; color: #555; border-left: 4px solid #ff2442; }}
.tag {{ display: inline-block; background: #fff0f0; color: #ff2442; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 4px; }}
.footer {{ background: #fafafa; padding: 20px; text-align: center; font-size: 12px; color: #999; }}
.dest-info {{ display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }}
.dest-info span {{ font-size: 13px; color: #666; }}
.dest-info span strong {{ color: #333; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🦞 每日小红书旅游攻略</h1>
    <div class="date">{today} · 今日推荐：{dest['name']}</div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">📍</span>景点信息</div>
    <div class="dest-info">
      <span><strong>景点：</strong>{dest['name']}</span>
      <span><strong>省份：</strong>{dest['province']}</span>
      <span><strong>类型：</strong>{dest['type']}</span>
      <span><strong>建议行程：</strong>{days_text}</span>
    </div>
    <div style="font-size: 14px; color: #666; line-height: 1.6;">
      {dest['highlight']}
    </div>
    <div style="margin-top: 12px;">
      {''.join(f'<span class="tag">{tag}</span>' for tag in dest['tags'])}
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">📝</span>小红书文案</div>
    <div style="font-size: 16px; font-weight: 700; color: #ff2442; margin-bottom: 12px;">{title}</div>
    <div class="content-text">{content.replace(chr(10), '<br>')}</div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">🎨</span>DALL-E 3 海报提示词</div>
    <div style="font-size: 13px; color: #666; margin-bottom: 12px;">
      复制以下内容到 ChatGPT image2 / DALL-E 3 生成主视角海报：
    </div>
    <div class="prompt-box">{dalle_prompt}</div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">🍜</span>必吃美食</div>
    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
      {''.join(f'<span class="tag">{food}</span>' for food in dest['foods'])}
    </div>
  </div>

  <div class="footer">
    <div>🦞 权权养的虾（小红书）每日推送</div>
    <div style="margin-top: 4px;">每天晚上11点，为你解锁一个国内宝藏目的地</div>
  </div>
</div>
</body>
</html>"""
    return html


def send_email(subject, html_body):
    """发送邮件（通过QQ邮箱SMTP）"""
    import ssl
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465
    SMTP_USER = "569545015@qq.com"
    SMTP_PASS = "iylylmwnitbbbebi"
    TO_EMAIL = "569545015@qq.com"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        # 发件人显示名：权权养的虾（小红书）
        sender_name_b64 = "=?utf-8?b?5p2D5p2D5YW755qE6Jm+77yI5bCP5LiA566h5a6277yJ?="
        msg['From'] = f"{sender_name_b64} <{SMTP_USER}>"
        msg['To'] = TO_EMAIL

        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}", file=sys.stderr)
        return False


def main():
    # 随机选择景点（小众景点权重更高）
    weights = [3 if d["type"] == "小众" else 1 for d in DESTINATIONS]
    dest = random.choices(DESTINATIONS, weights=weights, k=1)[0]

    # 生成内容
    title, xhs_content = generate_xiaohongshu_content(dest)
    dalle_prompt = generate_dalle_prompt(dest)

    # 生成邮件
    html = generate_email_html(dest, title, xhs_content, dalle_prompt)

    # 发送邮件
    subject = f"🦞 每日攻略 | {dest['name']} · {title[:20]}..."
    success = send_email(subject, html)

    # 输出日志
    status = "✅ 已发送" if success else "❌ 发送失败"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {status} | 今日景点: {dest['name']} ({dest['province']}) | 类型: {dest['type']} | 行程: {dest['days']}天")

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
