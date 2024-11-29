import pandas as pd
from zhipuai import ZhipuAI
from autogluon.timeseries.dataset.ts_dataframe import TimeSeriesDataFrame

# Define breakpoints for pollutants based on EPA standards.
breakpoints_pm25 = [
    {'AQI_low': 0, 'AQI_high': 50, 'Conc_low': 0.0, 'Conc_high': 9.0},
    {'AQI_low': 51, 'AQI_high': 100, 'Conc_low': 9.1, 'Conc_high': 35.4},
    {'AQI_low': 101, 'AQI_high': 150, 'Conc_low': 35.5, 'Conc_high': 55.4},
    {'AQI_low': 151, 'AQI_high': 200, 'Conc_low': 55.5, 'Conc_high': 125.4},
    {'AQI_low': 201, 'AQI_high': 300, 'Conc_low': 125.5, 'Conc_high': 225.4},
    {'AQI_low': 301, 'AQI_high': 9999, 'Conc_low': 225.5, 'Conc_high': 9999}
]
breakpoints_pm10 = [
    {'AQI_low': 0, 'AQI_high': 50, 'Conc_low': 0, 'Conc_high': 54},
    {'AQI_low': 51, 'AQI_high': 100, 'Conc_low': 55, 'Conc_high': 154},
    {'AQI_low': 101, 'AQI_high': 150, 'Conc_low': 155, 'Conc_high': 254},
    {'AQI_low': 151, 'AQI_high': 200, 'Conc_low': 255, 'Conc_high': 354},
    {'AQI_low': 201, 'AQI_high': 300, 'Conc_low': 355, 'Conc_high': 424},
    {'AQI_low': 301, 'AQI_high': 9999, 'Conc_low': 425, 'Conc_high': 9999}
]
breakpoints_co = [
    {'AQI_low': 0, 'AQI_high': 50, 'Conc_low': 0.0, 'Conc_high': 4.4},
    {'AQI_low': 51, 'AQI_high': 100, 'Conc_low': 4.5, 'Conc_high': 9.4},
    {'AQI_low': 101, 'AQI_high': 150, 'Conc_low': 9.5, 'Conc_high': 12.4},
    {'AQI_low': 151, 'AQI_high': 200, 'Conc_low': 12.5, 'Conc_high': 15.4},
    {'AQI_low': 201, 'AQI_high': 300, 'Conc_low': 15.5, 'Conc_high': 30.4},
    {'AQI_low': 301, 'AQI_high': 9999, 'Conc_low': 30.5, 'Conc_high': 9999}
]
breakpoints_so2 = [
    {'AQI_low': 0, 'AQI_high': 50, 'Conc_low': 0, 'Conc_high': 35},
    {'AQI_low': 51, 'AQI_high': 100, 'Conc_low': 36, 'Conc_high': 75},
    {'AQI_low': 101, 'AQI_high': 150, 'Conc_low': 76, 'Conc_high': 185},
    {'AQI_low': 151, 'AQI_high': 200, 'Conc_low': 186, 'Conc_high': 304},
    {'AQI_low': 201, 'AQI_high': 300, 'Conc_low': 305, 'Conc_high': 604},
    {'AQI_low': 301, 'AQI_high': 9999, 'Conc_low': 605, 'Conc_high': 9999}
]
breakpoints_no2 = [
    {'AQI_low': 0, 'AQI_high': 50, 'Conc_low': 0, 'Conc_high': 53},
    {'AQI_low': 51, 'AQI_high': 100, 'Conc_low': 54, 'Conc_high': 100},
    {'AQI_low': 101, 'AQI_high': 150, 'Conc_low': 101, 'Conc_high': 360},
    {'AQI_low': 151, 'AQI_high': 200, 'Conc_low': 361, 'Conc_high': 649},
    {'AQI_low': 201, 'AQI_high': 300, 'Conc_low': 650, 'Conc_high': 1249},
    {'AQI_low': 301, 'AQI_high': 9999, 'Conc_low': 1250, 'Conc_high': 9999}
]
breakpoints_o3 = [
    {'AQI_low': 0, 'AQI_high': 50, 'Conc_low': 0.0, 'Conc_high': 0.054},
    {'AQI_low': 51, 'AQI_high': 100, 'Conc_low': 0.055, 'Conc_high': 0.070},
    {'AQI_low': 101, 'AQI_high': 150, 'Conc_low': 0.071, 'Conc_high': 0.085},
    {'AQI_low': 151, 'AQI_high': 200, 'Conc_low': 0.086, 'Conc_high': 0.105},
    {'AQI_low': 201, 'AQI_high': 300, 'Conc_low': 0.106, 'Conc_high': 0.200},
    {'AQI_low': 301, 'AQI_high': 9999, 'Conc_low': 0.201, 'Conc_high': 9999.000}
]


def calc_single_aqi(concentration, breakpoints):
    for bp in breakpoints:
        if bp['Conc_low'] <= concentration <= bp['Conc_high']:
            aqi_low, aqi_high = bp['AQI_low'], bp['AQI_high']
            conc_low, conc_high = bp['Conc_low'], bp['Conc_high']
            aqi = ((aqi_high - aqi_low) / (conc_high - conc_low)) * (concentration - conc_low) + aqi_low
            return round(aqi)
    return None  # Out of range


# 确保value在0和9999之间
def clamp(value):
    return max(0, min(9999, value))


def calculate_aqi(pollutants):
    if all(value is None for value in pollutants.values()):
        raise ValueError(f"All parameters are NONE, can NOT calc AQI.")
    # Calculate AQI for each pollutant.
    aqi_results = {}
    for pollutant, concentration in pollutants.items():
        #concentration = None if math.isnan(concentration) else concentration    # 去除 nan
        concentration = None if concentration is None else clamp(concentration) # 约束参数范围
        if pollutant == 'pm25' and not concentration is None:
            concentration = round(concentration, 1)     # 保留小数点
            aqi_results[pollutant] = calc_single_aqi(concentration, breakpoints_pm25)
        elif pollutant == 'pm10' and not concentration is None:
            concentration = round(concentration)
            aqi_results[pollutant] = calc_single_aqi(concentration, breakpoints_pm10)
        elif pollutant == 'co' and not concentration is None:
            concentration = round(concentration, 1)
            aqi_results[pollutant] = calc_single_aqi(concentration, breakpoints_co)
        elif pollutant == 'so2' and not concentration is None:
            concentration = round(concentration)
            aqi_results[pollutant] = calc_single_aqi(concentration, breakpoints_so2)
        elif pollutant == 'no2' and not concentration is None:
            concentration = round(concentration)
            aqi_results[pollutant] = calc_single_aqi(concentration, breakpoints_no2)
        elif pollutant == 'o3' and not concentration is None:
            concentration = round(concentration, 3)
            aqi_results[pollutant] = calc_single_aqi(concentration, breakpoints_o3)
    # print("--->>", pollutants)
    # print("===>>", aqi_results)
    return max(value for value in aqi_results.values() if value is not None)


def gen_pic(city, aqi, is_healthy, healthy_color, healthy_status):
    pic_prompt = f'请以 {city} 市区最著名的景点为背景，生成一幅空气质量指数为 {aqi}，对人体 {is_healthy} 的图片，图片中请用Arial字体添加文字 "AQI: {aqi} {healthy_status}"，文字的底色为 {healthy_color}'
    client = ZhipuAI(api_key="89b799c8de44de7b2a7bb1986986a126.EHWbBI3SjVsegxkX")
    response = client.images.generations(
        model="cogview-3-plus", #模型编码
        prompt=pic_prompt,
    )
    # 返回图片url
    return response.data[0].url


# 函数：根据输入日期，进行 AQI 预测
def predict_aqi(input_date, data, predictor):
    # 确保输入日期为 pandas 的 datetime 格式
    input_date = pd.to_datetime(input_date)

    # 确认是否有足够的历史数据
    start_date = input_date - pd.Timedelta(days=3)
    if start_date not in data['timestamp'].values:
        raise ValueError("历史数据不足，无法预测，请确保输入日期的前3天有数据")

    # 提取前3天的历史数据
    history_data = data[(data['timestamp'] >= start_date) & (data['timestamp'] < input_date)]
    if len(history_data) != 3:
        raise ValueError("前3天的历史数据不完整，无法预测")

    # 构造预测输入
    # 注意：TimeSeriesDataFrame 需要目标值，即使是 NaN，也要在预测时指定
    future_date = pd.DataFrame({
        'timestamp': [input_date],
        'AQI': [None]  # 占位
    })
    prediction_input = pd.concat([history_data, future_date], ignore_index=True)
    
    # 字段改名
    prediction_input = prediction_input.rename(columns={'AQI': 'target'})
    prediction_input['item_id'] = 'default'

    # 转换为 TimeSeriesDataFrame 格式
    prediction_input = TimeSeriesDataFrame.from_data_frame(
        prediction_input,
        timestamp_column='timestamp',
        #target_column='AQI'
    )

    # 使用模型进行预测
    predictions = predictor.predict(prediction_input)

    # 获取预测值
    predicted_mean = predictions['mean'].iloc[0]
    predicted_quantiles = predictions.iloc[0, 3:]  # 获取不确定性区间

    return {
        "predicted_mean": predicted_mean,
        "quantiles": predicted_quantiles.to_dict()
    }