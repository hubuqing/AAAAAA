import requests
from flask import current_app
from datetime import datetime, timezone, timedelta

class GenieACS:
    def __init__(self):
        self.base_url = current_app.config['GENIEACS_URL']
        self.auth = (current_app.config['GENIEACS_USERNAME'], 
                    current_app.config['GENIEACS_PASSWORD'])

    def _get_beijing_time(self, utc_time_str):
        """将UTC时间转换为北京时间"""
        try:
            # 解析UTC时间
            utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            # 转换为北京时间（固定8小时偏移）
            return utc_time + timedelta(hours=8)
        except Exception as e:
            current_app.logger.error(f"Error converting to Beijing time: {str(e)}")
            return None

    def _normalize_device(self, device):
        """标准化设备数据"""
        try:
            device_id = device.get('_id')
            device_info = device.get('_deviceId', {})
            
            # 获取制造商
            manufacturer = device_info.get('_Manufacturer', 'Unknown')
            
            # 获取型号
            model = device_info.get('_ProductClass', 'Unknown')
            
            # 获取固件版本
            firmware_version = device_info.get('_SoftwareVersion', 'Unknown')
            
            # 获取最后在线时间
            last_seen = None
            last_inform = device.get('_lastInform')
            current_app.logger.info(f"Device {device_id} last_inform: {last_inform}")
            if last_inform:
                try:
                    # 解析UTC时间并添加时区信息
                    utc_time = datetime.strptime(last_inform, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                    # 转换为北京时间并去掉时区信息
                    beijing_time = utc_time.astimezone(timezone(timedelta(hours=8)))
                    last_seen = beijing_time.replace(tzinfo=None)
                    current_app.logger.info(f"Device {device_id} last_seen (Beijing): {last_seen}")
                except Exception as e:
                    current_app.logger.error(f"Error parsing last_seen time: {str(e)}")
            
            # 判断设备状态
            status = 'offline'
            if last_inform:
                try:
                    utc_time = datetime.strptime(last_inform, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                    current_utc = datetime.now(timezone.utc)
                    time_diff = current_utc - utc_time
                    if time_diff.total_seconds() <= 600:  # 10分钟内在线
                        status = 'online'
                    current_app.logger.info(f"Device {device_id} status: {status}, time_diff: {time_diff.total_seconds()}s")
                except Exception as e:
                    current_app.logger.error(f"Error determining device status: {str(e)}")
            
            # 获取IP地址
            ip_address = device.get('InternetGatewayDevice', {}).get('WANDevice', {}).get('1', {}).get('WANConnectionDevice', {}).get('1', {}).get('WANIPConnection', {}).get('1', {}).get('ExternalIPAddress', 'Unknown')
            
            # 获取MAC地址
            mac_address = device.get('InternetGatewayDevice', {}).get('WANDevice', {}).get('1', {}).get('WANConnectionDevice', {}).get('1', {}).get('WANIPConnection', {}).get('1', {}).get('MACAddress', 'Unknown')
            
            # 获取注册时间
            registered = None
            reg_time = device.get('_registered')
            current_app.logger.info(f"Device {device_id} registered: {reg_time}")
            if reg_time:
                try:
                    utc_time = datetime.strptime(reg_time, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                    beijing_time = utc_time.astimezone(timezone(timedelta(hours=8)))
                    registered = beijing_time.replace(tzinfo=None)
                    current_app.logger.info(f"Device {device_id} registered (Beijing): {registered}")
                except Exception as e:
                    current_app.logger.error(f"Error parsing registered time: {str(e)}")
            
            # 获取最后启动时间
            last_boot = None
            events = device.get('Events', [])
            for event in events:
                if event.get('_type') == 'Inform':
                    timestamp = event.get('_timestamp')
                    current_app.logger.info(f"Device {device_id} last_boot timestamp: {timestamp}")
                    if timestamp:
                        try:
                            utc_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                            beijing_time = utc_time.astimezone(timezone(timedelta(hours=8)))
                            last_boot = beijing_time.replace(tzinfo=None)
                            current_app.logger.info(f"Device {device_id} last_boot (Beijing): {last_boot}")
                        except Exception as e:
                            current_app.logger.error(f"Error parsing last_boot time: {str(e)}")
                    break
            
            # 获取OUI
            oui = device_info.get('_OUI', 'Unknown')
            
            # 获取产品类别
            product_class = device_info.get('_ProductClass', 'Unknown')
            
            return {
                'device_id': device_id,
                'manufacturer': manufacturer,
                'model': model,
                'firmware_version': firmware_version,
                'last_seen': last_seen,
                'status': status,
                'ip_address': ip_address,
                'mac_address': mac_address,
                'registered': registered,
                'last_boot': last_boot,
                'oui': oui,
                'product_class': product_class
            }
        except Exception as e:
            current_app.logger.error(f"Error normalizing device data: {str(e)}")
            return None

    def get_devices(self):
        """获取所有设备列表"""
        try:
            url = f"{self.base_url}/devices"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            devices = response.json()
            return [self._normalize_device(device) for device in devices]
        except Exception as e:
            current_app.logger.error(f"Error fetching devices: {str(e)}")
            return []

    def get_device(self, device_id):
        """获取单个设备详情"""
        try:
            url = f"{self.base_url}/devices/{device_id}"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            device = response.json()
            return self._normalize_device(device)
        except Exception as e:
            current_app.logger.error(f"Error fetching device {device_id}: {str(e)}")
            return None

    def get_device_parameters(self, device_id):
        """获取设备参数"""
        try:
            url = f"{self.base_url}/devices/{device_id}/parameters"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Error fetching parameters for device {device_id}: {str(e)}")
            return {}

    def set_parameter(self, device_id, parameter, value):
        """设置设备参数"""
        try:
            url = f"{self.base_url}/devices/{device_id}/parameters"
            data = {
                "parameter": parameter,
                "value": value
            }
            response = requests.post(url, json=data, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Error setting parameter for device {device_id}: {str(e)}")
            return None

    def reboot_device(self, device_id):
        """重启设备"""
        try:
            url = f"{self.base_url}/devices/{device_id}/reboot"
            response = requests.post(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Error rebooting device {device_id}: {str(e)}")
            return None

    def factory_reset(self, device_id):
        """恢复出厂设置"""
        try:
            url = f"{self.base_url}/devices/{device_id}/factory_reset"
            response = requests.post(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f"Error factory resetting device {device_id}: {str(e)}")
            return None 