"""
Database models and initialization for Algae Box System
Using SQLAlchemy with SQLite
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Database file path
DB_PATH = 'algae_box.db'
DATABASE_URL = f'sqlite:///{DB_PATH}'


class Tank(Base):
    """Tank/cultivation system information"""
    __tablename__ = 'tanks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    algae_type = Column(String(50), nullable=False)
    volume_liters = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='active')  # active, maintenance, inactive
    notes = Column(Text)
    
    # Relationships
    sensor_readings = relationship('SensorReading', back_populates='tank', cascade='all, delete-orphan')
    collection_events = relationship('CollectionEvent', back_populates='tank', cascade='all, delete-orphan')
    user_actions = relationship('UserAction', back_populates='tank', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Tank(id={self.id}, name='{self.name}', algae='{self.algae_type}')>"


class SensorReading(Base):
    """Sensor data readings"""
    __tablename__ = 'sensor_readings'
    
    id = Column(Integer, primary_key=True)
    tank_id = Column(Integer, ForeignKey('tanks.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # Sensor values
    ph = Column(Float)
    temperature_c = Column(Float)
    turbidity_ntu = Column(Float)
    
    # Status flags
    ph_safe = Column(Boolean)
    temperature_safe = Column(Boolean)
    harvest_ready = Column(Boolean)
    
    # Relationship
    tank = relationship('Tank', back_populates='sensor_readings')
    
    def __repr__(self):
        return f"<SensorReading(tank={self.tank_id}, time={self.timestamp}, pH={self.ph:.2f}, turb={self.turbidity_ntu:.1f})>"


class CollectionEvent(Base):
    """Algae collection/harvest events"""
    __tablename__ = 'collection_events'
    
    id = Column(Integer, primary_key=True)
    tank_id = Column(Integer, ForeignKey('tanks.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # Collection details
    duration_seconds = Column(Integer)
    success = Column(Boolean)
    turbidity_before = Column(Float)
    turbidity_after = Column(Float)
    estimated_amount_ml = Column(Float)
    notes = Column(Text)
    
    # Relationship
    tank = relationship('Tank', back_populates='collection_events')
    
    def __repr__(self):
        return f"<CollectionEvent(tank={self.tank_id}, time={self.timestamp}, success={self.success})>"


class AlgaeSpecies(Base):
    """Algae species cultivation requirements"""
    __tablename__ = 'algae_species'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    scientific_name = Column(String(100))
    
    # Optimal ranges
    ph_min = Column(Float, nullable=False)
    ph_max = Column(Float, nullable=False)
    ph_optimal = Column(Float)
    
    temp_min_c = Column(Float, nullable=False)
    temp_max_c = Column(Float, nullable=False)
    temp_optimal_c = Column(Float)
    
    # Harvest criteria
    harvest_turbidity_ntu = Column(Float, nullable=False)
    growth_rate_days = Column(Integer)  # Days to harvest
    
    # Additional info
    description = Column(Text)
    uses = Column(Text)  # Commercial uses
    difficulty = Column(String(20))  # easy, moderate, hard
    
    def __repr__(self):
        return f"<AlgaeSpecies(name='{self.name}', pH={self.ph_min}-{self.ph_max})>"


class UserAction(Base):
    """User actions and maintenance log"""
    __tablename__ = 'user_actions'
    
    id = Column(Integer, primary_key=True)
    tank_id = Column(Integer, ForeignKey('tanks.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    action_type = Column(String(50), nullable=False)  # ph_adjustment, nutrient_add, cleaning, etc.
    description = Column(Text)
    notes = Column(Text)
    
    # Relationship
    tank = relationship('Tank', back_populates='user_actions')
    
    def __repr__(self):
        return f"<UserAction(tank={self.tank_id}, type='{self.action_type}', time={self.timestamp})>"


class Database:
    """Database management class"""
    
    def __init__(self, db_url=DATABASE_URL):
        """Initialize database connection"""
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        print(f"✅ Database initialized: {DB_PATH}")
        
        # Seed algae species if empty
        session = self.Session()
        if session.query(AlgaeSpecies).count() == 0:
            self.seed_algae_species(session)
        session.close()
    
    def seed_algae_species(self, session):
        """Add default algae species data"""
        species_data = [
            {
                'name': 'Spirulina',
                'scientific_name': 'Arthrospira platensis',
                'ph_min': 8.0, 'ph_max': 11.0, 'ph_optimal': 9.5,
                'temp_min_c': 30, 'temp_max_c': 40, 'temp_optimal_c': 35,
                'harvest_turbidity_ntu': 400,
                'growth_rate_days': 7,
                'description': 'Blue-green algae, high protein content',
                'uses': 'Nutritional supplements, protein powder',
                'difficulty': 'moderate'
            },
            {
                'name': 'Chlorella',
                'scientific_name': 'Chlorella vulgaris',
                'ph_min': 6.0, 'ph_max': 7.5, 'ph_optimal': 6.8,
                'temp_min_c': 20, 'temp_max_c': 30, 'temp_optimal_c': 25,
                'harvest_turbidity_ntu': 300,
                'growth_rate_days': 5,
                'description': 'Green algae, fast growing, nutrient-dense',
                'uses': 'Health supplements, detoxification',
                'difficulty': 'easy'
            },
            {
                'name': 'Nannochloropsis',
                'scientific_name': 'Nannochloropsis oculata',
                'ph_min': 7.5, 'ph_max': 9.0, 'ph_optimal': 8.2,
                'temp_min_c': 20, 'temp_max_c': 30, 'temp_optimal_c': 25,
                'harvest_turbidity_ntu': 350,
                'growth_rate_days': 8,
                'description': 'Marine algae, high lipid content',
                'uses': 'Biodiesel, omega-3 production, aquaculture feed',
                'difficulty': 'moderate'
            },
            {
                'name': 'Haematococcus',
                'scientific_name': 'Haematococcus pluvialis',
                'ph_min': 7.0, 'ph_max': 8.0, 'ph_optimal': 7.5,
                'temp_min_c': 20, 'temp_max_c': 28, 'temp_optimal_c': 24,
                'harvest_turbidity_ntu': 250,
                'growth_rate_days': 14,
                'description': 'Red algae, produces astaxanthin',
                'uses': 'Astaxanthin production, antioxidant supplements',
                'difficulty': 'hard'
            },
            {
                'name': 'Dunaliella',
                'scientific_name': 'Dunaliella salina',
                'ph_min': 7.5, 'ph_max': 9.5, 'ph_optimal': 8.5,
                'temp_min_c': 25, 'temp_max_c': 35, 'temp_optimal_c': 30,
                'harvest_turbidity_ntu': 320,
                'growth_rate_days': 10,
                'description': 'Halophilic algae, beta-carotene production',
                'uses': 'Beta-carotene, cosmetics, food coloring',
                'difficulty': 'moderate'
            }
        ]
        
        for data in species_data:
            species = AlgaeSpecies(**data)
            session.add(species)
        
        session.commit()
        print(f"✅ Seeded {len(species_data)} algae species")
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()


# Global database instance
db = Database()


if __name__ == "__main__":
    """Initialize database when run directly"""
    print("Initializing Algae Box Database...")
    db.init_db()
    
    # Display seeded species
    session = db.get_session()
    species = session.query(AlgaeSpecies).all()
    print(f"\n📋 Available Algae Species ({len(species)}):")
    for s in species:
        print(f"  - {s.name}: pH {s.ph_min}-{s.ph_max}, {s.temp_min_c}-{s.temp_max_c}°C, harvest @ {s.harvest_turbidity_ntu} NTU")
    session.close()
    
    print("\n✅ Database ready!")
