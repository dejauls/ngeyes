from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from calendar import monthrange
from datetime import datetime, timedelta

client = MongoClient('mongodb://belajar:belajar@ac-pewhlve-shard-00-00.m1k88nt.mongodb.net:27017,ac-pewhlve-shard-00-01.m1k88nt.mongodb.net:27017,ac-pewhlve-shard-00-02.m1k88nt.mongodb.net:27017/?ssl=true&replicaSet=atlas-i3tctf-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0')
db = client.linkc

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/link", methods=["POST"])
def link_post():
    try:
        platform = request.form['platform']
        print(f"Received platform: {platform}") 
        
        current_time = datetime.now().strftime('%Y-%m-%d')  
        doc = {
            'platform': platform,
            'timestamp': current_time  
        }

        result = db.link.insert_one(doc)
        print(f"Document inserted with id: {result.inserted_id}")  # Debug: Print insertion result

        return jsonify({'msg': 'POST request received!'})
    except Exception as e:
        print(f"Error: {e}")  # Debug: Print any error that occurs
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

@app.route('/view_data', methods=['GET'])
def view_data():
    try:
        date = request.args.get('date')
        query = {}
        if date:
            query['timestamp'] = date
        
        data = list(db.link.find(query, {'_id': 0, 'platform': 1, 'timestamp': 1}))
        return render_template('index.html', data=data)
    except Exception as e:
        print(f"Error: {e}")  # Debug: Print any error that occurs
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500
    
@app.route('/data_today', methods=['GET'])
def data_today():
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        data = list(db.link.find({'timestamp': today}, {'_id': 0, 'platform': 1, 'timestamp': 1}))
        return jsonify(data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500    
    
# @app.route('/data_month', methods=['GET'])
# def data_month():
#     try:
#         today = datetime.today()
#         first_day_of_month = today.replace(day=1)
#         data = list(db.link.find({'timestamp': {'$gte': first_day_of_month.strftime('%Y-%m-%d')}}, {'_id': 0, 'platform': 1, 'timestamp': 1}))
#         return jsonify(data)
#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

@app.route('/data_week', methods=['GET'])
def data_week():
    try:
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        data = list(db.link.find({'timestamp': {'$gte': start_of_week.strftime('%Y-%m-%d')}}, {'_id': 0, 'platform': 1, 'timestamp': 1}))
        return jsonify(data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500    

@app.route('/data_range', methods=['GET'])
def data_range():
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify({'msg': 'Start date and end date are required'}), 400
        
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        platforms = ['instagram', 'whatsapp', 'tiktok', 'youtube', 'website', 'berita', 'artikel']
        counts = {}

        for platform in platforms:
            count = db.link.count_documents({
                'platform': platform,
                'timestamp': {'$gte': start_date, '$lt': end_date_obj.strftime('%Y-%m-%d')}
            })
            counts[platform] = count
        
        return jsonify(counts)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

def get_month_data(year, month):
    num_days = monthrange(year, month)[1]
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime(year, month, num_days).strftime('%Y-%m-%d')

    pipeline = [
        {"$match": {
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "platform": {"$exists": True, "$ne": ""}
        }},
        {"$group": {
            "_id": {"platform": "$platform", "date": "$timestamp"},
            "count": {"$sum": 1}
        }}
    ]

    data = list(db.link.aggregate(pipeline))

    # Prepare chart data structure
    chart_data = {}

    # Initialize data structure with all days of the month
    for platform in ['artikel', 'berita', 'instagram', 'tiktok', 'website', 'whatsapp', 'youtube']:
        chart_data[platform] = {
            'labels': [datetime(year, month, day).strftime('%Y-%m-%d') for day in range(1, num_days + 1)],
            'data': [0] * num_days
        }

    # Fill data from MongoDB results
    for entry in data:
        platform = entry['_id'].get('platform')
        if not platform:
            continue

        date = entry['_id']['date']
        count = entry['count']

        if date in chart_data[platform]['labels']:
            index = chart_data[platform]['labels'].index(date)
            chart_data[platform]['data'][index] = count

    return chart_data

@app.route('/data_month', methods=['GET'])
def data_month():
    try:
        month = request.args.get('month')
        year = request.args.get('year')

        if not month or not year:
            return jsonify({'msg': 'Month and year parameters are required'}), 400

        month = int(month)
        year = int(year)

        chart_data = get_month_data(year, month)

        return jsonify(chart_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500
    

# Example platform list (customize as per your actual platforms)
PLATFORMS = ['instagram', 'whatsApp', 'tiktok', 'youTube', 'artikel', 'berita', 'website']

@app.route('/data_year', methods=['GET'])
def data_year():
    try:
        year = request.args.get('year')

        if not year:
            return jsonify({'msg': 'Year parameter is required'}), 400

        year = int(year)
        
        # Initialize platform counts for each month
        monthly_data = {month: {platform: 0 for platform in PLATFORMS} for month in range(1, 13)}
        
        # Prepare pipeline to aggregate data grouped by month and platform
        pipeline = [
            {"$match": {
                "timestamp": {
                    "$gte": datetime(year, 1, 1),  # Start of the year
                    "$lt": datetime(year + 1, 1, 1)  # Start of the next year
                }
            }},
            {"$group": {
                "_id": {"month": {"$month": "$timestamp"}, "platform": "$platform"},
                "count": {"$sum": 1}
            }}
        ]

        data = list(db.collection.aggregate(pipeline))

        # Update monthly_data with actual counts
        for entry in data:
            month = entry['_id']['month']
            platform = entry['_id']['platform']
            count = entry['count']
            monthly_data[month][platform] = count

        # Prepare final response
        chart_data = [{'month': month, 'counts': monthly_data[month]} for month in range(1, 13)]

        return jsonify(chart_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

    
@app.route('/instagram_count', methods=['GET'])
def instagram_count():
    try:
        count = db.link.count_documents({'platform': 'instagram'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500    
    
@app.route('/whatsapp_count', methods=['GET'])
def whatsapp_count():
    try:
        count = db.link.count_documents({'platform': 'whatsapp'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500   

@app.route('/tiktok_count', methods=['GET'])
def tiktok_count():
    try:
        count = db.link.count_documents({'platform': 'tiktok'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500        

@app.route('/youtube_count', methods=['GET'])
def youtube_count():
    try:
        count = db.link.count_documents({'platform': 'youtube'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

@app.route('/website_count', methods=['GET'])
def website_count():
    try:
        count = db.link.count_documents({'platform': 'website'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

@app.route('/berita_count', methods=['GET'])
def berita_count():
    try:
        count = db.link.count_documents({'platform': 'berita'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

@app.route('/artikel_count', methods=['GET'])
def artikel_count():
    try:
        count = db.link.count_documents({'platform': 'artikel'})
        return jsonify({'count': count})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
