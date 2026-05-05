import pandas as pd

def process_signal_data(file_path):
    """
    读取并处理 5G 信号数据。
    包含预处理逻辑和为前端准备的地图颜色计算。
    """
    df = pd.read_csv(file_path)
    
    # 核心要求：地图上的点根据信号强度(RSRP_dBm)变色
    # > -90dBm 为绿色, < -110dBm 为红色, 其余为黄色
    def get_color(rsrp):
        if rsrp > -90:
            return [0, 255, 0, 160]   # 绿
        elif rsrp < -110:
            return [255, 0, 0, 160]   # 红
        else:
            return [255, 255, 0, 160] # 黄
            
    df['color'] = df['RSRP_dBm'].apply(get_color)
    return df
