import unittest
import pandas as pd
from data_processor import process_signal_data
import os

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        # 创建一个临时测试数据文件
        self.test_file = "test_data.csv"
        df = pd.DataFrame({
            "Latitude": [31.2, 31.3, 31.4],
            "Longitude": [121.4, 121.5, 121.6],
            "CellID": [1, 2, 3],
            "Band": ["n41", "n78", "n28"],
            "RSRP_dBm": [-80, -100, -120],  # 分别对应: 绿, 黄, 红
            "SINR_dB": [10, 5, 0],
            "TerminalType": ["Smartphone", "CPE", "IoT"],
            "Download_Mbps": [500, 100, 20]
        })
        df.to_csv(self.test_file, index=False)

    def tearDown(self):
        # 清理临时文件
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_process_signal_data(self):
        """测试数据处理和颜色分配逻辑"""
        df = process_signal_data(self.test_file)
        
        # 检查是否成功返回 DataFrame
        self.assertFalse(df.empty)
        
        # 检查颜色逻辑
        # rsrp = -80 > -90, 应为绿色
        self.assertEqual(df.iloc[0]['color'], [0, 255, 0, 160])
        
        # rsrp = -100 在 -110 和 -90 之间, 应为黄色
        self.assertEqual(df.iloc[1]['color'], [255, 255, 0, 160])
        
        # rsrp = -120 < -110, 应为红色
        self.assertEqual(df.iloc[2]['color'], [255, 0, 0, 160])

if __name__ == '__main__':
    unittest.main()
