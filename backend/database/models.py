from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Anchor(Base):
    __tablename__ = 'anchors'

    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # What the user called it
    name = Column(String, nullable=False, index=True) 
    
    description = Column(String) 
    
    # Location data (center point normalized to 0-100)
    x_center = Column(Float, nullable=False)
    y_center = Column(Float, nullable=False)
    
    # implement later feature_vector = Column(BLOB) 
    
    def __repr__(self):
        return f"Anchor(id={self.id}, name='{self.name}', coords=({self.x_center:.2f}, {self.y_center:.2f}))"
