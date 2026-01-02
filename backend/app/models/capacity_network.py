from sqlalchemy import Column, Integer, String, Float, Sequence
from app.core.database import Base

class CapacityNetworkValues(Base):
    __tablename__ = "capacity_network_values"
    
    id = Column(Integer, Sequence('capacity_network_values_seq'), primary_key=True)
    device_name = Column(String(255))
    mean_cpu = Column(Float)
    peak_cpu = Column(Float)
    mean_memory = Column(Float)
    peak_memory = Column(Float)
    cpu_date = Column(String(255))
    cpu_time = Column(String(255))
    memory_date = Column(String(255))
    memory_time = Column(String(255))
    cpu_alert_duration = Column(Float)
    memory_alert_duration = Column(Float)
    ntimes_cpu = Column(Integer)
    ntimes_memory = Column(Integer)

class RegionZoneMappingNetwork(Base):
    __tablename__ = "region_zone_mapping_network"

    id = Column(Integer, Sequence('region_zone_mapping_network_seq'), primary_key=True)
    region_name = Column(String(100), nullable=False)
    zone_name = Column(String(255), nullable=False)

class ZoneDeviceMappingNetwork(Base):
    __tablename__ = "zone_device_mapping_network"

    id = Column(Integer, Sequence('zone_device_mapping_network_seq'), primary_key=True)
    zone_name = Column(String(255), nullable=False)
    device_name = Column(String(255), nullable=False)