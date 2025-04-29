from flask import Blueprint, render_template, jsonify, request, flash
from flask_login import login_required
from app.utils.genieacs import GenieACS
from flask import current_app
import json

bp = Blueprint('devices', __name__)

@bp.route('/devices')
@login_required
def device_list():
    try:
        genieacs = GenieACS()
        devices = genieacs.get_devices()
        if not devices:
            current_app.logger.warning("没有找到任何设备")
            flash('当前没有可用的设备', 'info')
        return render_template('devices/list.html', devices=devices)
    except Exception as e:
        current_app.logger.error(f"获取设备列表失败: {str(e)}")
        flash('获取设备列表时发生错误，请检查 GenieACS 服务是否正常运行', 'error')
        return render_template('devices/list.html', devices=[])

@bp.route('/devices/<device_id>')
@login_required
def device_detail(device_id):
    try:
        current_app.logger.info(f"Accessing device detail page for device_id: {device_id}")
        
        genieacs = GenieACS()
        device = genieacs.get_device(device_id)
        
        if not device:
            current_app.logger.error(f"设备不存在或获取失败: {device_id}")
            flash('设备不存在或已被删除', 'error')
            return render_template('devices/detail.html', device=None, parameters=[])
            
        current_app.logger.info(f"Successfully retrieved device: {json.dumps(device, ensure_ascii=False)}")
        
        parameters = genieacs.get_device_parameters(device_id)
        if not parameters:
            current_app.logger.warning(f"设备 {device_id} 没有可用的参数")
        else:
            current_app.logger.info(f"Retrieved {len(parameters)} parameters for device")
            
        return render_template('devices/detail.html', 
                             device=device, 
                             parameters=parameters)
    except Exception as e:
        current_app.logger.error(f"获取设备详情失败: {str(e)}")
        flash('获取设备信息时发生错误，请稍后重试', 'error')
        return render_template('devices/detail.html', device=None, parameters=[]), 500

@bp.route('/devices/<device_id>/reboot', methods=['POST'])
@login_required
def reboot_device(device_id):
    genieacs = GenieACS()
    result = genieacs.reboot_device(device_id)
    return jsonify(result)

@bp.route('/devices/<device_id>/factory-reset', methods=['POST'])
@login_required
def factory_reset(device_id):
    genieacs = GenieACS()
    result = genieacs.factory_reset(device_id)
    return jsonify(result)

@bp.route('/devices/<device_id>/parameters', methods=['POST'])
@login_required
def set_parameter(device_id):
    genieacs = GenieACS()
    parameter = request.json.get('parameter')
    value = request.json.get('value')
    result = genieacs.set_parameter(device_id, parameter, value)
    return jsonify(result)

@bp.route('/api/devices')
def get_devices_api():
    """获取设备列表的API端点"""
    try:
        genieacs = GenieACS()
        devices = genieacs.get_devices()
        return jsonify({
            'success': True,
            'devices': devices
        })
    except Exception as e:
        current_app.logger.error(f"获取设备列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 