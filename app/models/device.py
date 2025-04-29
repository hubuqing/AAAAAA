from app import db
from datetime import datetime

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False)
    manufacturer = db.Column(db.String(64))
    model = db.Column(db.String(64))
    firmware_version = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='offline')
    ip_address = db.Column(db.String(45))
    mac_address = db.Column(db.String(17))
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'firmware_version': self.firmware_version,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'status': self.status,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address
        } 