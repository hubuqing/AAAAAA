from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.utils.genieacs import GenieACS
from flask import current_app

bp = Blueprint('devices', __name__)

@bp.route('/devices')
@login_required
def device_list():
    genieacs = GenieACS()
    devices = genieacs.get_devices()
    return render_template('devices/list.html', devices=devices)

@bp.route('/devices/<device_id>')
@login_required
def device_detail(device_id):
    genieacs = GenieACS()
    device = genieacs.get_device(device_id)
    parameters = genieacs.get_device_parameters(device_id)
    return render_template('devices/detail.html', 
                         device=device, 
                         parameters=parameters)

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