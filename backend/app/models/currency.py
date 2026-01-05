"""
Currency Rate Model for TCMB integration
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func

from app.database import Base


class CurrencyRate(Base):
    """Currency exchange rates from TCMB"""
    __tablename__ = "currency_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    currency_code = Column(String(3), nullable=False, index=True)  # USD, EUR
    
    # Rates
    buying_rate = Column(Numeric(15, 6), nullable=False)
    selling_rate = Column(Numeric(15, 6), nullable=False)
    effective_buying = Column(Numeric(15, 6))  # Efektif alış
    effective_selling = Column(Numeric(15, 6))  # Efektif satış
    
    # Date
    rate_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CurrencyRate {self.currency_code}: {self.selling_rate}>"
