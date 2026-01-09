from sqlalchemy import Column, Integer, String, Date, Text, Sequence
from app.core.database import Base

class FirewallBackup(Base):
    __tablename__ = "SUMMARY_TABLE_FIREWALL_LOGS_BACKUP_NEW"

    # Using specific sequence if needed, otherwise default auto-increment
    id = Column(Integer, Sequence('firewall_backup_id_seq'), primary_key=True, index=True)
    task_date = Column(Date, nullable=False)
    task_name = Column(String(255), nullable=False)
    host_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    # Using Text for CLOB fields as per SQLAlchemy mapping
    failed_hosts = Column(Text, nullable=True)
    successful_hosts = Column(Text, nullable=True)
