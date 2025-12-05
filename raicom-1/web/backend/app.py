"""
垃圾分类科普知识平台 - Flask后端API
提供垃圾分类查询、知识库、统计等接口
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
import http.client
import urllib.parse

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db_manager import db_manager
from question.question_bank import QuestionBank
import random

app = Flask(__name__)
CORS(app)  # 允许跨域请求


# 全局异常处理器，防止后端崩溃
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"全局异常捕获: {str(e)}")
    return jsonify({"success": False, "message": f"服务器内部错误: {str(e)}"}), 500

# 垃圾分类数据库
GARBAGE_DATABASE = {
    "可回收物": {
        "description": "可回收物是指适宜回收利用和资源化利用的生活废弃物，主要包括废纸、塑料、玻璃、金属和布料五大类",
        "color": "#3498db",
        "icon": "♻️",
        "items": [
            {"name": "塑料瓶", "tips": "清空内容物，压扁投放"},
            {"name": "废纸", "tips": "保持干燥，避免污染"},
            {"name": "玻璃瓶", "tips": "清洗干净，小心轻放"},
            {"name": "易拉罐", "tips": "压扁后投放"},
            {"name": "旧衣物", "tips": "清洗干净，打包投放"},
            {"name": "纸箱", "tips": "拆开压平"},
            {"name": "书本", "tips": "捆扎整齐"},
            {"name": "金属罐", "tips": "清洗后投放"},
            {"name": "报纸", "tips": "叠放整齐，避免受潮"},
            {"name": "杂志", "tips": "去除塑料封面后投放"},
            {"name": "牛奶盒", "tips": "清洗干净，压扁投放"},
            {"name": "饮料瓶", "tips": "去除瓶盖，压扁投放"},
            {"name": "旧书包", "tips": "清空内容物后投放"},
            {"name": "铁锅", "tips": "清洗干净后投放"},
            {"name": "铝制品", "tips": "压扁后投放"},
        ]
    },
    "有害垃圾": {
        "description": "有害垃圾是指对人体健康或自然环境造成直接或潜在危害的废弃物，需要特殊安全处理",
        "color": "#e74c3c",
        "icon": "☠️",
        "items": [
            {"name": "废电池", "tips": "单独收集，不要混入其他垃圾"},
            {"name": "废灯管", "tips": "小心轻放，避免破碎"},
            {"name": "过期药品", "tips": "连同包装一起投放"},
            {"name": "油漆桶", "tips": "密封后投放"},
            {"name": "杀虫剂", "tips": "连同容器一起投放"},
            {"name": "温度计", "tips": "小心轻放，避免破碎"},
            {"name": "过期化妆品", "tips": "连同包装一起投放"},
            {"name": "指甲油", "tips": "连同瓶子一起投放"},
            {"name": "消毒液", "tips": "连同容器一起投放"},
            {"name": "农药瓶", "tips": "清洗后单独投放"},
        ]
    },
    "厨余垃圾": {
        "description": "厨余垃圾是指居民日常生活及食品加工等过程中产生的废弃物，可通过堆肥转化为有机肥料",
        "color": "#27ae60",
        "icon": "🍎",
        "items": [
            {"name": "剩菜剩饭", "tips": "沥干水分后投放"},
            {"name": "果皮果核", "tips": "直接投放"},
            {"name": "蛋壳", "tips": "直接投放"},
            {"name": "茶叶渣", "tips": "沥干水分"},
            {"name": "菜叶菜根", "tips": "直接投放"},
            {"name": "过期食品", "tips": "去除包装后投放"},
            {"name": "鱼骨", "tips": "直接投放"},
            {"name": "虾壳", "tips": "直接投放"},
            {"name": "花生壳", "tips": "直接投放"},
            {"name": "瓜子壳", "tips": "直接投放"},
            {"name": "豆腐渣", "tips": "沥干水分后投放"},
            {"name": "中药渣", "tips": "沥干水分后投放"},
        ]
    },
    "其他垃圾": {
        "description": "其他垃圾是指除可回收物、有害垃圾、厨余垃圾以外的其他生活废弃物，一般采用焚烧或填埋处理",
        "color": "#95a5a6",
        "icon": "🗑️",
        "items": [
            {"name": "卫生纸", "tips": "直接投放"},
            {"name": "烟蒂", "tips": "熄灭后投放"},
            {"name": "陶瓷碎片", "tips": "包裹后投放"},
            {"name": "一次性餐具", "tips": "清洗后投放"},
            {"name": "尘土", "tips": "直接投放"},
            {"name": "污染纸张", "tips": "直接投放"},
            {"name": "大骨头", "tips": "直接投放，难以降解"},
            {"name": "贝壳", "tips": "直接投放"},
            {"name": "椰子壳", "tips": "直接投放，太硬难降解"},
            {"name": "胶带", "tips": "直接投放"},
            {"name": "创可贴", "tips": "直接投放"},
            {"name": "旧毛巾", "tips": "污染严重的直接投放"},
        ]
    }
}

# 科普知识库
KNOWLEDGE_BASE = [
    {
        "id": 1,
        "title": "为什么要进行垃圾分类？",
        "content": "垃圾分类可以减少垃圾处理量和处理设备，降低处理成本，减少土地资源的消耗。同时，垃圾分类可以变废为宝，提高资源利用率，减少环境污染。据统计，通过垃圾分类可以回收利用约30%的生活垃圾，大大减少了资源浪费。",
        "category": "基础知识",
        "tags": ["环保", "基础"]
    },
    {
        "id": 2,
        "title": "可回收物有哪些？",
        "content": "可回收物主要包括五大类：1.废纸类（报纸、杂志、书本、纸箱等）；2.塑料类（塑料瓶、塑料袋、塑料玩具等）；3.玻璃类（玻璃瓶、玻璃杯、镜子等）；4.金属类（易拉罐、铁罐、铜制品等）；5.布料类（旧衣服、床单、毛巾等）。投放前请清洗干净。",
        "category": "分类指南",
        "tags": ["可回收物", "分类"]
    },
    {
        "id": 3,
        "title": "有害垃圾的危害",
        "content": "有害垃圾如果处理不当，会对土壤、水源造成严重污染，危害人体健康。例如，一节废电池可以污染60万升水，一个废灯管可以污染数吨土壤。有害垃圾必须单独收集、专门处理，切勿混入其他垃圾。",
        "category": "环保知识",
        "tags": ["有害垃圾", "危害"]
    },
    {
        "id": 4,
        "title": "厨余垃圾如何处理？",
        "content": "厨余垃圾应该沥干水分后投放到厨余垃圾桶。投放前需去除包装物，如塑料袋、保鲜膜等。厨余垃圾可以通过堆肥等方式转化为有机肥料，实现资源化利用，是很好的土壤改良剂。",
        "category": "分类指南",
        "tags": ["厨余垃圾", "处理"]
    },
    {
        "id": 5,
        "title": "垃圾分类的四大原则",
        "content": "1.分而用之：分类的目的是提高资源利用率；2.因地制宜：根据当地情况制定分类标准；3.自觉自治：每个人都应该自觉参与；4.循序渐进：逐步完善分类体系。记住这四个原则，垃圾分类就不难了。",
        "category": "基础知识",
        "tags": ["原则", "基础"]
    },
    {
        "id": 6,
        "title": "垃圾桶颜色的含义",
        "content": "不同颜色的垃圾桶代表不同的垃圾类型：蓝色代表可回收物，红色代表有害垃圾，绿色代表厨余垃圾，灰色代表其他垃圾。记住颜色对应关系，投放垃圾时就不会出错了。",
        "category": "基础知识",
        "tags": ["垃圾桶", "颜色"]
    },
    {
        "id": 7,
        "title": "塑料袋属于什么垃圾？",
        "content": "干净的塑料袋属于可回收物，但被污染的塑料袋（如装过食物残渣的）属于其他垃圾。投放厨余垃圾时，需要将垃圾倒出，塑料袋单独投放到其他垃圾桶。",
        "category": "分类指南",
        "tags": ["塑料袋", "分类"]
    },
    {
        "id": 8,
        "title": "外卖餐盒如何分类？",
        "content": "外卖餐盒的分类取决于其材质和清洁程度：清洗干净的塑料餐盒属于可回收物；被油污严重污染的餐盒属于其他垃圾；餐盒里的剩菜剩饭属于厨余垃圾。建议先将食物残渣倒入厨余垃圾，再处理餐盒。",
        "category": "分类指南",
        "tags": ["外卖", "餐盒"]
    },
    {
        "id": 9,
        "title": "电子产品如何处理？",
        "content": "废旧电子产品（如手机、电脑、充电器等）属于可回收物，但其中的电池属于有害垃圾。处理时应将电池取出单独投放到有害垃圾桶，电子产品本体投放到可回收物桶或交给专业回收机构。",
        "category": "分类指南",
        "tags": ["电子产品", "回收"]
    },
    {
        "id": 10,
        "title": "垃圾分类的环保意义",
        "content": "垃圾分类是实现垃圾减量化、资源化、无害化的重要途径。通过分类，可回收物得到再利用，有害垃圾得到安全处理，厨余垃圾转化为肥料，大大减少了填埋和焚烧量，保护了我们的环境。",
        "category": "环保知识",
        "tags": ["环保", "意义"]
    },
]

# 环保资讯数据
NEWS_DATA = [
    {
        "id": 1,
        "title": "全国垃圾分类工作取得显著成效",
        "category": "政策法规",
        "date": "2024-12-01",
        "source": "环保部",
        "summary": "截至2024年底，全国地级及以上城市生活垃圾分类覆盖率已超过90%。"
    },
    {
        "id": 2,
        "title": "智能垃圾分类设备助力社区环保",
        "category": "环保科技",
        "date": "2024-11-28",
        "source": "科技日报",
        "summary": "新型AI智能垃圾分类设备在多个城市试点应用，准确率达95%以上。"
    },
    {
        "id": 3,
        "title": "世界环境日：共建清洁美丽世界",
        "category": "环保行动",
        "date": "2024-11-20",
        "source": "新华网",
        "summary": "全国各地开展丰富多彩的环保宣传活动。"
    },
    {
        "id": 4,
        "title": "新版《生活垃圾分类标志》标准发布",
        "category": "政策法规",
        "date": "2024-11-15",
        "source": "住建部",
        "summary": "统一了全国垃圾分类标志的图形符号、颜色和文字说明。"
    },
    {
        "id": 5,
        "title": "可降解塑料技术取得重大突破",
        "category": "环保科技",
        "date": "2024-11-10",
        "source": "科学网",
        "summary": "新型可降解塑料材料可在自然环境中3个月内完全降解。"
    },
    {
        "id": 6,
        "title": "青年志愿者开展垃圾分类宣传活动",
        "category": "环保行动",
        "date": "2024-11-05",
        "source": "中国青年报",
        "summary": "通过互动游戏、知识讲座等形式普及环保知识。"
    }
]


# ========== API路由 ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "message": "服务运行正常"})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有垃圾分类"""
    categories = []
    for name, data in GARBAGE_DATABASE.items():
        categories.append({
            "name": name,
            "description": data["description"],
            "color": data["color"],
            "icon": data["icon"],
            "itemCount": len(data["items"])
        })
    return jsonify({"success": True, "data": categories})


@app.route('/api/category/<name>', methods=['GET'])
def get_category_detail(name):
    """获取分类详情"""
    if name in GARBAGE_DATABASE:
        data = GARBAGE_DATABASE[name]
        return jsonify({
            "success": True,
            "data": {
                "name": name,
                "description": data["description"],
                "color": data["color"],
                "icon": data["icon"],
                "items": data["items"]
            }
        })
    return jsonify({"success": False, "message": "分类不存在"}), 404


@app.route('/api/search', methods=['GET'])
def search_garbage():
    """搜索垃圾分类 - 使用天行API"""
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"success": False, "message": "请输入搜索关键词"}), 400
    
    # 调用天行API
    try:
        conn = http.client.HTTPSConnection('apis.tianapi.com')
        params = urllib.parse.urlencode({
            'key': '95bdf1f58892fff912c9e983896e5d3b',
            'word': keyword
        })
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        conn.request('POST', '/lajifenlei/index', params, headers)
        response = conn.getresponse()
        result = response.read().decode('utf-8')
        api_data = json.loads(result)
        conn.close()
        
        if api_data.get('code') == 200 and api_data.get('result'):
            # 分类颜色映射
            category_colors = {
                '可回收物': '#3498db',
                '有害垃圾': '#e74c3c',
                '厨余垃圾': '#27ae60',
                '湿垃圾': '#27ae60',
                '其他垃圾': '#95a5a6',
                '干垃圾': '#95a5a6'
            }
            
            results = []
            for item in api_data['result'].get('list', []):
                name = item.get('name', '')
                category = item.get('type', '未知分类')
                # 统一分类名称
                if category == '湿垃圾':
                    category = '厨余垃圾'
                elif category == '干垃圾':
                    category = '其他垃圾'
                
                results.append({
                    "name": name,
                    "category": category,
                    "color": category_colors.get(category, '#95a5a6'),
                    "icon": get_category_icon(category),
                    "tips": item.get('explain', ''),
                    "contain": item.get('contain', ''),
                    "tip": item.get('tip', '')
                })
            
            return jsonify({"success": True, "data": results, "count": len(results)})
        else:
            # API没有结果，使用本地数据库搜索
            return search_local_garbage(keyword)
            
    except Exception as e:
        print(f"天行API调用失败: {e}")
        # 降级到本地搜索
        return search_local_garbage(keyword)


def get_category_icon(category):
    """获取分类图标"""
    icons = {
        '可回收物': '♻️',
        '有害垃圾': '☠️',
        '厨余垃圾': '🍎',
        '湿垃圾': '🍎',
        '其他垃圾': '🗑️',
        '干垃圾': '🗑️'
    }
    return icons.get(category, '🗑️')


def search_local_garbage(keyword):
    """本地数据库搜索（备用）"""
    results = []
    for category, data in GARBAGE_DATABASE.items():
        for item in data["items"]:
            if keyword.lower() in item["name"].lower():
                results.append({
                    "name": item["name"],
                    "category": category,
                    "color": data["color"],
                    "icon": data["icon"],
                    "tips": item["tips"]
                })
    return jsonify({"success": True, "data": results, "count": len(results)})


# ========== 高德地图API ==========
AMAP_WEB_KEY = '166b3fc546c25f9c10d422c5a6f34f14'


@app.route('/api/amap/nearby', methods=['GET'])
def amap_nearby_search():
    """搜索附近的垃圾桶/垃圾站/环卫设施"""
    try:
        lng = request.args.get('lng', '')
        lat = request.args.get('lat', '')
        
        if not lng or not lat:
            return jsonify({"success": False, "message": "缺少经纬度参数"})
        
        all_bins = []
        
        # 多个关键词搜索，提高命中率
        keywords_list = ['垃圾站', '垃圾分类', '环卫', '废品回收', '再生资源']
        
        for keyword in keywords_list:
            try:
                conn = http.client.HTTPSConnection('restapi.amap.com')
                params = urllib.parse.urlencode({
                    'key': AMAP_WEB_KEY,
                    'location': f'{lng},{lat}',
                    'keywords': keyword,
                    'radius': 5000,  # 扩大到5公里
                    'offset': 10,
                    'sortrule': 'distance'
                })
                
                conn.request('GET', f'/v5/place/around?{params}')
                response = conn.getresponse()
                result = response.read().decode('utf-8')
                api_data = json.loads(result)
                conn.close()
                
                if api_data.get('status') == '1' and api_data.get('pois'):
                    for poi in api_data['pois']:
                        location = poi.get('location', '').split(',')
                        if len(location) == 2:
                            name = poi.get('name', '')
                            # 避免重复
                            if not any(b['name'] == name for b in all_bins):
                                all_bins.append({
                                    'name': name,
                                    'address': poi.get('address', '') or poi.get('pname', '') + poi.get('cityname', ''),
                                    'lng': float(location[0]),
                                    'lat': float(location[1]),
                                    'distance': int(poi.get('distance', 0)),
                                    'type': poi.get('type', '')
                                })
            except Exception as e:
                print(f"搜索关键词 {keyword} 失败: {e}")
                continue
        
        # 按距离排序
        all_bins.sort(key=lambda x: x['distance'])
        
        return jsonify({"success": True, "data": all_bins[:20]})  # 最多返回20个
            
    except Exception as e:
        print(f"高德API调用失败: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route('/api/amap/regeo', methods=['GET'])
def amap_regeo():
    """逆地理编码 - 根据经纬度获取地址"""
    try:
        lng = request.args.get('lng', '')
        lat = request.args.get('lat', '')
        
        if not lng or not lat:
            return jsonify({"success": False, "message": "缺少经纬度参数"})
        
        conn = http.client.HTTPSConnection('restapi.amap.com')
        params = urllib.parse.urlencode({
            'key': AMAP_WEB_KEY,
            'location': f'{lng},{lat}'
        })
        
        conn.request('GET', f'/v3/geocode/regeo?{params}')
        response = conn.getresponse()
        result = response.read().decode('utf-8')
        api_data = json.loads(result)
        conn.close()
        
        if api_data.get('status') == '1':
            address = api_data.get('regeocode', {}).get('formatted_address', '')
            return jsonify({"success": True, "address": address})
        else:
            return jsonify({"success": False, "message": "获取地址失败"})
            
    except Exception as e:
        print(f"逆地理编码失败: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route('/api/amap/geocode', methods=['GET'])
def amap_geocode():
    """地理编码 - 根据地址获取经纬度"""
    try:
        address = request.args.get('address', '')
        
        if not address:
            return jsonify({"success": False, "message": "缺少地址参数"})
        
        conn = http.client.HTTPSConnection('restapi.amap.com')
        params = urllib.parse.urlencode({
            'key': AMAP_WEB_KEY,
            'address': address
        })
        
        conn.request('GET', f'/v3/geocode/geo?{params}')
        response = conn.getresponse()
        result = response.read().decode('utf-8')
        api_data = json.loads(result)
        conn.close()
        
        if api_data.get('status') == '1' and api_data.get('geocodes'):
            geo = api_data['geocodes'][0]
            location = geo.get('location', '').split(',')
            if len(location) == 2:
                return jsonify({
                    "success": True,
                    "lng": float(location[0]),
                    "lat": float(location[1]),
                    "address": geo.get('formatted_address', '')
                })
        
        return jsonify({"success": False, "message": "未找到该地址"})
            
    except Exception as e:
        print(f"地理编码失败: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """获取环保资讯 - 使用天行API"""
    try:
        num = request.args.get('num', 10, type=int)
        
        conn = http.client.HTTPSConnection('apis.tianapi.com')
        params = urllib.parse.urlencode({
            'key': '95bdf1f58892fff912c9e983896e5d3b',
            'num': num
        })
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        conn.request('POST', '/huanbao/index', params, headers)
        response = conn.getresponse()
        result = response.read().decode('utf-8')
        api_data = json.loads(result)
        conn.close()
        
        print(f"天行API返回: code={api_data.get('code')}, msg={api_data.get('msg')}")
        
        if api_data.get('code') == 200 and api_data.get('result'):
            news_list = []
            result_data = api_data['result']
            # 天行API返回的是 newslist
            items = result_data.get('newslist', []) if isinstance(result_data, dict) else result_data
            
            for idx, item in enumerate(items):
                news_list.append({
                    "id": idx + 1,
                    "title": item.get('title', ''),
                    "content": item.get('description', '') or item.get('content', ''),
                    "category": "环保资讯",
                    "tags": ["环保", "资讯"],
                    "source": item.get('source', ''),
                    "url": item.get('url', ''),
                    "time": item.get('ctime', '') or item.get('time', ''),
                    "imgUrl": item.get('picUrl', '') or item.get('imgUrl', '')
                })
            print(f"解析到 {len(news_list)} 条资讯")
            return jsonify({"success": True, "data": news_list})
        else:
            # API失败，返回本地数据
            print(f"API返回失败，使用本地数据")
            return jsonify({"success": True, "data": KNOWLEDGE_BASE})
            
    except Exception as e:
        print(f"天行环保API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": True, "data": KNOWLEDGE_BASE})


@app.route('/api/knowledge/<int:id>', methods=['GET'])
def get_knowledge_detail(id):
    """获取知识详情（保留兼容）"""
    for item in KNOWLEDGE_BASE:
        if item["id"] == id:
            return jsonify({"success": True, "data": item})
    return jsonify({"success": False, "message": "知识不存在"}), 404


@app.route('/api/news', methods=['GET'])
def get_news():
    """获取环保资讯列表"""
    category = request.args.get('category', '')
    if category:
        filtered = [n for n in NEWS_DATA if n["category"] == category]
        return jsonify({"success": True, "data": filtered})
    return jsonify({"success": True, "data": NEWS_DATA})


@app.route('/api/news/<int:id>', methods=['GET'])
def get_news_detail(id):
    """获取资讯详情"""
    for item in NEWS_DATA:
        if item["id"] == id:
            return jsonify({"success": True, "data": item})
    return jsonify({"success": False, "message": "资讯不存在"}), 404


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    quiz_count = db_manager.get_quiz_count()
    return jsonify({
        "success": True,
        "data": {
            "categoryCount": len(GARBAGE_DATABASE),
            "itemCount": "90000+",  # 天行API垃圾分类数据量
            "newsCount": 10,  # 环保资讯默认显示10条
            "quizCount": quiz_count
        }
    })


# ========== 题库相关API ==========

@app.route('/api/quiz/questions', methods=['GET'])
def get_quiz_questions():
    """获取随机题目"""
    try:
        limit = request.args.get('limit', 10, type=int)
        questions = db_manager.get_quiz_questions(limit=limit)
        return jsonify({"success": True, "data": questions, "count": len(questions)})
    except Exception as e:
        print(f"获取题目失败: {e}")
        return jsonify({"success": True, "data": [], "count": 0})


# ========== 反馈相关API ==========

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交检测结果反馈"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"}), 400
        
        garbage_name = data.get('garbage_name', '')
        predicted_category = data.get('predicted_category', '')
        is_correct = data.get('is_correct', True)
        correct_category = data.get('correct_category')
        satisfaction = data.get('satisfaction')
        feedback_comment = data.get('feedback_comment')
        detection_id = data.get('detection_id')
        
        if not garbage_name or not predicted_category:
            return jsonify({"success": False, "message": "垃圾名称和预测分类不能为空"}), 400
        
        # 确保数据库连接
        if not db_manager.connection or not db_manager.connection.is_connected():
            if not db_manager.connect():
                return jsonify({"success": False, "message": "数据库连接失败"}), 500
        
        success = db_manager.save_feedback(
            garbage_name=garbage_name,
            predicted_category=predicted_category,
            is_correct=is_correct,
            correct_category=correct_category,
            satisfaction=satisfaction,
            feedback_comment=feedback_comment,
            detection_id=detection_id
        )
        
        if success:
            return jsonify({"success": True, "message": "反馈提交成功"})
        else:
            return jsonify({"success": False, "message": "反馈提交失败"}), 500
            
    except Exception as e:
        print(f"提交反馈错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """获取反馈统计数据"""
    try:
        # 确保数据库连接
        if not db_manager.connection or not db_manager.connection.is_connected():
            if not db_manager.connect():
                return jsonify({"success": True, "data": {
                    "total_feedback": 0,
                    "correct_count": 0,
                    "incorrect_count": 0,
                    "accuracy_rate": 0,
                    "avg_satisfaction": 0,
                    "category_stats": [],
                    "satisfaction_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                }})
        stats = db_manager.get_feedback_stats()
        return jsonify({"success": True, "data": stats if stats else {}})
    except Exception as e:
        print(f"获取统计失败: {str(e)}")
        return jsonify({"success": True, "data": {}})


@app.route('/api/feedback/list', methods=['GET'])
def get_feedback_list():
    """获取反馈列表"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 确保数据库连接
        if not db_manager.connection or not db_manager.connection.is_connected():
            if not db_manager.connect():
                return jsonify({"success": True, "data": []})
        
        feedback_list = db_manager.get_feedback_list(limit=limit, offset=offset)
        return jsonify({"success": True, "data": feedback_list if feedback_list else []})
    except Exception as e:
        print(f"获取反馈列表失败: {str(e)}")
        return jsonify({"success": True, "data": []})


@app.route('/api/feedback/detection-ids', methods=['GET'])
def get_feedback_detection_ids():
    """获取所有已反馈的检测记录ID"""
    try:
        ids = db_manager.get_feedback_detection_ids()
        return jsonify({"success": True, "data": ids})
    except Exception as e:
        print(f"获取已反馈ID失败: {str(e)}")
        return jsonify({"success": True, "data": []})


@app.route('/api/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    """删除反馈记录"""
    try:
        success = db_manager.delete_feedback(feedback_id)
        if success:
            return jsonify({"success": True, "message": "删除成功"})
        else:
            return jsonify({"success": False, "message": "删除失败"}), 404
    except Exception as e:
        print(f"删除反馈失败: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/detection/history', methods=['GET'])
def get_detection_history():
    """获取检测历史记录"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 确保数据库连接
        try:
            if not db_manager.connection or not db_manager.connection.is_connected():
                if not db_manager.connect():
                    return jsonify({"success": True, "data": []})
        except Exception:
            if not db_manager.connect():
                return jsonify({"success": True, "data": []})
        
        history = db_manager.get_detection_history(limit=limit, offset=offset)
        
        # 格式化返回数据
        formatted_history = []
        for record in history:
            formatted_history.append({
                'id': record['id'],
                'image_path': record['image_path'],
                'detection_results': record['detection_results'],
                'detection_time': record['detection_time'].strftime('%Y-%m-%d %H:%M:%S') if record['detection_time'] else '',
                'confidence_scores': record['confidence_scores'],
                'processing_time': record['processing_time'],
                'source_type': record['source_type']
            })
        
        return jsonify({"success": True, "data": formatted_history})
    except Exception as e:
        print(f"获取历史记录错误: {str(e)}")
        return jsonify({"success": True, "data": [], "message": f"数据库连接失败: {str(e)}"})


if __name__ == '__main__':
    print("=" * 50)
    print("垃圾分类科普知识平台 - 后端API")
    print("=" * 50)
    
    # 初始化数据库连接
    print("正在连接数据库...")
    if db_manager.connect():
        print("数据库连接成功!")
    else:
        print("警告: 数据库连接失败，反馈功能可能不可用")
    
    print(f"API地址: http://localhost:5000")
    print("=" * 50)
    # debug=True 但禁用 reloader，避免重复启动
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
