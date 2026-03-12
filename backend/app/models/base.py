from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime, timedelta, timezone
from ..core.database import Base

CHINA_TZ = timezone(timedelta(hours=8))

def get_now():
    return datetime.now(CHINA_TZ)
