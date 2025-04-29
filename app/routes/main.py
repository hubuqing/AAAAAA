from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.genieacs import GenieACS
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    genieacs = GenieACS()
    devices = genieacs.get_devices()
    return render_template('index.html', 
                         devices=devices,
                         now=datetime.utcnow(),
                         timedelta=timedelta)

@bp.route('/dashboard')
@login_required
def dashboard():
    genieacs = GenieACS()
    devices = genieacs.get_devices()
    return render_template('dashboard.html', 
                         devices=devices,
                         now=datetime.utcnow(),
                         timedelta=timedelta) 