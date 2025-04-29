from datetime import datetime
import pytz

def _normalize_device(device):
    """Normalize device data from GenieACS."""
    if not device:
        return None
        
    # 获取UTC时间
    last_inform_time = device.get('_lastInform', '')
    if last_inform_time:
        try:
            # 解析UTC时间
            utc_time = datetime.fromisoformat(last_inform_time.replace('Z', '+00:00'))
            
            # 转换到北京时间
            beijing_tz = pytz.timezone('Asia/Shanghai')
            beijing_time = utc_time.astimezone(beijing_tz)
            
            # 格式化时间显示
            device['_lastInform'] = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 判断设备状态
            current_time = datetime.now(pytz.UTC)
            time_diff = current_time - utc_time
            device['_deviceStatus'] = '在线' if time_diff.total_seconds() <= 600 else '离线'
            
        except Exception as e:
            # 如果时间转换出错，保留原始时间
            device['_lastInform'] = last_inform_time
            device['_deviceStatus'] = '未知'

    return device

class GenieACSAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        
    def get_devices(self):
        # ... 其他代码 ...
        pass 