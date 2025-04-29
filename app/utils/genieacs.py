import requests
from flask import current_app
from datetime import datetime
import pytz
import json
from urllib.parse import quote

class GenieACS:
    def __init__(self):
        self.base_url = current_app.config['GENIEACS_URL']
        self.auth = (current_app.config['GENIEACS_USERNAME'], 
                    current_app.config['GENIEACS_PASSWORD'])
        self.beijing_tz = pytz.timezone('Asia/Shanghai')

    def _convert_to_beijing_time(self, utc_time_str):
        """将UTC时间转换为北京时间"""
        try:
            if not utc_time_str:
                current_app.logger.warning("Empty UTC time string received")
                return None
                
            # 记录原始时间字符串
            current_app.logger.info(f"Converting time - Original UTC time: {utc_time_str}")
            
            # 尝试解析不同的时间格式
            try:
                utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
                current_app.logger.info("Successfully parsed time using fromisoformat")
            except ValueError as e:
                current_app.logger.warning(f"Failed to parse with fromisoformat: {e}")
                try:
                    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    current_app.logger.info("Successfully parsed time using strptime with microseconds")
                except ValueError as e:
                    current_app.logger.warning(f"Failed to parse with microseconds format: {e}")
                    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
                    current_app.logger.info("Successfully parsed time using strptime without microseconds")
            
            # 转换为北京时间
            beijing_time = utc_time.astimezone(self.beijing_tz)
            formatted_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 记录转换后的时间
            current_app.logger.info(f"Time conversion successful - Beijing time: {formatted_time}")
            
            return formatted_time
        except Exception as e:
            current_app.logger.error(f"Time conversion error: {str(e)}, Original time: {utc_time_str}")
            return utc_time_str

    def _normalize_device(self, device):
        """标准化设备数据"""
        if not device:
            current_app.logger.warning("Empty device data received")
            return None
            
        # 记录原始设备数据
        current_app.logger.info(f"Normalizing device - Original data: {json.dumps(device, ensure_ascii=False)}")
        
        # 处理最后在线时间
        last_inform_time = device.get('_lastInform', '')
        current_app.logger.info(f"Processing last inform time: {last_inform_time}")
        
        if last_inform_time:
            device['_lastInform'] = self._convert_to_beijing_time(last_inform_time)
            
            try:
                utc_time = datetime.fromisoformat(last_inform_time.replace('Z', '+00:00'))
                current_time = datetime.now(pytz.UTC)
                time_diff = current_time - utc_time
                
                # 记录时间差
                seconds_diff = time_diff.total_seconds()
                current_app.logger.info(f"Time difference from now: {seconds_diff} seconds")
                
                device['_deviceStatus'] = '在线' if seconds_diff <= 600 else '离线'
                current_app.logger.info(f"Device status set to: {device['_deviceStatus']}")
            except Exception as e:
                current_app.logger.error(f"Error determining device status: {str(e)}")
                device['_deviceStatus'] = '未知'

        # 处理注册时间
        registered_time = device.get('_registered', '')
        if registered_time:
            device['_registered'] = self._convert_to_beijing_time(registered_time)
            current_app.logger.info(f"Processed registration time: {device['_registered']}")

        # 记录处理后的设备数据
        current_app.logger.info(f"Device normalization complete - Final data: {json.dumps(device, ensure_ascii=False)}")
        return device

    def get_devices(self):
        """获取所有设备列表"""
        try:
            url = f"{self.base_url}/devices"
            current_app.logger.info(f"Fetching devices from: {url}")
            
            response = requests.get(url, auth=self.auth)
            current_app.logger.info(f"API Response Status: {response.status_code}")
            current_app.logger.info(f"API Response Headers: {dict(response.headers)}")
            
            # 记录原始响应
            try:
                response_data = response.json()
                current_app.logger.info(f"API Raw Response: {json.dumps(response_data, ensure_ascii=False)}")
            except Exception as e:
                current_app.logger.error(f"Failed to parse response as JSON: {str(e)}")
                current_app.logger.info(f"Raw response text: {response.text}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to fetch devices: Status {response.status_code}")
                current_app.logger.error(f"Response content: {response.text}")
                return []
                
            devices = response.json()
            if not devices:
                current_app.logger.warning("Empty device list returned from API")
                return []
                
            current_app.logger.info(f"Successfully fetched {len(devices)} devices")
            normalized_devices = [self._normalize_device(device) for device in devices]
            current_app.logger.info(f"Normalized devices: {json.dumps(normalized_devices, ensure_ascii=False)}")
            return normalized_devices
        except requests.exceptions.ConnectionError as e:
            current_app.logger.error(f"Connection error: {str(e)}")
            return []
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error: {str(e)}")
            return []
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            return []

    def get_device(self, device_id):
        """获取单个设备详情"""
        try:
            current_app.logger.info(f"Fetching device details for {device_id}")
            
            # 使用查询参数获取设备
            url = f"{self.base_url}/devices"
            params = {
                "query": json.dumps({"_id": device_id})
            }
            current_app.logger.info(f"Request URL: {url}, Params: {params}")
            
            response = requests.get(url, params=params, auth=self.auth)
            current_app.logger.info(f"Response status code: {response.status_code}")
            
            # 记录响应内容
            try:
                response_text = response.text
                current_app.logger.info(f"Response content: {response_text}")
            except Exception as e:
                current_app.logger.error(f"Failed to get response text: {str(e)}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to fetch device: Status {response.status_code}")
                return None
                
            devices = response.json()
            
            if not devices or len(devices) == 0:
                current_app.logger.error(f"No device found with ID {device_id}")
                return None
                
            device = devices[0]  # 获取第一个匹配的设备
            current_app.logger.info(f"Successfully fetched device {device_id}")
            current_app.logger.info(f"Raw device data: {json.dumps(device, ensure_ascii=False)}")
            
            normalized_device = self._normalize_device(device)
            current_app.logger.info(f"Normalized device data: {json.dumps(normalized_device, ensure_ascii=False)}")
            
            return normalized_device
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error fetching device {device_id}: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error fetching device {device_id}: {str(e)}")
            return None

    def get_device_parameters(self, device_id):
        """获取设备参数"""
        try:
            url = f"{self.base_url}/devices"
            params = {
                "query": json.dumps({"_id": device_id}),
                "projection": json.dumps(["_id", "InternetGatewayDevice"])
            }
            current_app.logger.info(f"Fetching parameters for device {device_id}")
            current_app.logger.info(f"Request URL: {url}, Params: {params}")
            
            response = requests.get(url, params=params, auth=self.auth)
            current_app.logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to fetch parameters: Status {response.status_code}")
                return []
                
            devices = response.json()
            if not devices or len(devices) == 0:
                current_app.logger.error(f"No device found with ID {device_id}")
                return []
                
            device = devices[0]
            parameters = []
            
            # 从设备数据中提取参数
            if 'InternetGatewayDevice' in device:
                for key, value in device['InternetGatewayDevice'].items():
                    parameters.append({
                        'name': f"InternetGatewayDevice.{key}",
                        'value': str(value),
                        'writable': True  # 默认可写
                    })
            
            current_app.logger.info(f"Retrieved {len(parameters)} parameters")
            return parameters
        except Exception as e:
            current_app.logger.error(f"Error fetching parameters for device {device_id}: {str(e)}")
            return []

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