import pandas as pd
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from autogluon.timeseries import TimeSeriesPredictor
from autogluon.timeseries.dataset.ts_dataframe import TimeSeriesDataFrame
from utils import calculate_aqi, predict_aqi, gen_pic

predict_bp = Blueprint('predict', __name__)

model_path = 'AutogluonModels/Liam/'
# 加载训练好的模型
predictor = TimeSeriesPredictor.load(model_path)


def inference(weather_data):
    # JSON转DateFrame
    weather_data_df = pd.DataFrame(weather_data).astype({'dewp': 'float64', 'wdsp': 'float64', 
        'max': 'float64', 'min': 'float64', 'prcp': 'float64', 'co': 'float64', 'no2': 'float64', 
        'o3': 'float64', 'pm10': 'float64', 'pm25': 'float64', 'so2': 'float64'})
    # 修改列名
    input_df = weather_data_df.rename(columns={'date': 'timestamp', 'dewp': 'DEWP', 
        'wdsp': 'WDSP', 'max': 'MAX', 'min': 'MIN', 'prcp': 'PRCP'})
    # 补充AQI
    input_df['AQI'] = input_df.apply(lambda row: calculate_aqi({
            'pm25': row.get('pm25', 0),
            'pm10': row.get('pm10', 0),
            'co':   row.get('co', 0),
            'so2':  row.get('so2', 0),
            'no2':  row.get('no2', 0),
            'o3':   row.get('o3', 0)
        }), axis=1)
    # 字段类型
    input_df['timestamp'] = pd.to_datetime(input_df['timestamp'])
    # 预测日期 获取下一天的日期并格式化为 'YYYY-MM-DD'
    input_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    result = predict_aqi(input_date, input_df, predictor)
    # print(f"预测日期 {input_date} 的 AQI 值为: {result['predicted_mean']:.2f}")
    # print(f"不确定性区间为: {result['quantiles']}")
    return round(result['predicted_mean'])


def aqi_categories(aqi):
    if 0 <= aqi <= 50:
        return ['Good', 'Green', 'Healty']
    elif 51 <= aqi <= 100:
        return ['Moderate', 'Yellow', 'Healty']
    elif 101 <= aqi <= 150:
        return ['Unhealthy for Sensitive Groups', 'Orange', 'Unhealthy']
    elif 151 <= aqi <= 200:
        return ['Unhealthy', 'Red', 'Unhealthy']
    elif 201 <= aqi <= 300:
        return ['Very Unhealthy', 'Purple', 'Unhealthy']
    elif aqi >= 301:
        return ['Hazardous', 'Maroon', 'Unhealthy']
    else:
        return ['Error', 'Error', 'Error']


@predict_bp.route('/predict', methods=['POST'])
def predict():
    # 获取请求中的数据
    data = request.get_json()
    city = data['city']
    weather_data = data['weatherData']
    predicted_aqi = inference(weather_data)
    # 获取AQI对应的健康状态
    healthy_status = aqi_categories(predicted_aqi)

    # 生成图片的URL
    # image_url = "https://via.placeholder.com/400x200?text=Prediction+Image"
    image_url = gen_pic(city, predicted_aqi, healthy_status[2], healthy_status[1], healthy_status[0])

    # 返回数据
    return jsonify({
        'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'aqi': f'{predicted_aqi} ({healthy_status[0]})',
        'healthyColor': healthy_status[1],
        'fontColor': 'black' if healthy_status[1] == 'Yellow' else 'white',
        'imageUrl': image_url
    })