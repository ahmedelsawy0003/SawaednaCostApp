from app.extensions import db
from datetime import datetime

class SequenceCounter(db.Model):
    """
    Model for generating unique sequential numbers for documents
    Format: PREFIX-YYYY-XXXX (e.g., MR-2025-0001)
    """
    __tablename__ = 'sequence_counter'
    
    id = db.Column(db.Integer, primary_key=True)
    prefix = db.Column(db.String(10), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    current_number = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('prefix', 'year', name='uq_prefix_year'),
    )
    
    def __repr__(self):
        return f'<SequenceCounter {self.prefix}-{self.year}: {self.current_number}>'
    
    @staticmethod
    def generate_number(prefix):
        """
        Generate a unique sequential number for the given prefix
        
        Args:
            prefix (str): Document prefix (e.g., 'MR', 'RT', 'PO', 'PY')
            
        Returns:
            str: Unique number in format PREFIX-YYYY-XXXX
        """
        current_year = datetime.now().year
        
        # Find or create counter for this prefix and year
        counter = SequenceCounter.query.filter_by(
            prefix=prefix,
            year=current_year
        ).with_for_update().first()
        
        if not counter:
            counter = SequenceCounter(
                prefix=prefix,
                year=current_year,
                current_number=1
            )
            db.session.add(counter)
        else:
            counter.current_number += 1
            counter.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Format: PREFIX-YYYY-XXXX
        return f"{prefix}-{current_year}-{counter.current_number:04d}"
    
    @staticmethod
    def get_next_number(prefix):
        """
        Preview the next number without incrementing the counter
        
        Args:
            prefix (str): Document prefix
            
        Returns:
            str: Next number that will be generated
        """
        current_year = datetime.now().year
        
        counter = SequenceCounter.query.filter_by(
            prefix=prefix,
            year=current_year
        ).first()
        
        next_num = (counter.current_number + 1) if counter else 1
        return f"{prefix}-{current_year}-{next_num:04d}"
    
    @staticmethod
    def reset_counter(prefix, year=None):
        """
        Reset counter for a specific prefix and year (admin function)
        
        Args:
            prefix (str): Document prefix
            year (int, optional): Year to reset. Defaults to current year.
        """
        if year is None:
            year = datetime.now().year
        
        counter = SequenceCounter.query.filter_by(
            prefix=prefix,
            year=year
        ).first()
        
        if counter:
            counter.current_number = 0
            counter.updated_at = datetime.utcnow()
            db.session.commit()

