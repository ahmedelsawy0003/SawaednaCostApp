"""
Utility functions for generating unique sequential numbers
"""

from app.models.sequence_counter import SequenceCounter

# Document prefixes
PREFIX_MATERIAL_REQUEST = 'MR'
PREFIX_MATERIAL_RETURN = 'RT'
PREFIX_PURCHASE_ORDER = 'PO'
PREFIX_PAYMENT_ORDER = 'PY'

def generate_material_request_number():
    """Generate unique number for Material Request"""
    return SequenceCounter.generate_number(PREFIX_MATERIAL_REQUEST)

def generate_material_return_number():
    """Generate unique number for Material Return"""
    return SequenceCounter.generate_number(PREFIX_MATERIAL_RETURN)

def generate_purchase_order_number():
    """Generate unique number for Purchase Order"""
    return SequenceCounter.generate_number(PREFIX_PURCHASE_ORDER)

def generate_payment_order_number():
    """Generate unique number for Payment Order"""
    return SequenceCounter.generate_number(PREFIX_PAYMENT_ORDER)

def get_next_material_request_number():
    """Preview next Material Request number"""
    return SequenceCounter.get_next_number(PREFIX_MATERIAL_REQUEST)

def get_next_material_return_number():
    """Preview next Material Return number"""
    return SequenceCounter.get_next_number(PREFIX_MATERIAL_RETURN)

def get_next_purchase_order_number():
    """Preview next Purchase Order number"""
    return SequenceCounter.get_next_number(PREFIX_PURCHASE_ORDER)

def get_next_payment_order_number():
    """Preview next Payment Order number"""
    return SequenceCounter.get_next_number(PREFIX_PAYMENT_ORDER)

