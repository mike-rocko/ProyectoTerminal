"""
Unit tests for helper functions.
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api.schedule import _horarios_conflictan, _normalizar_dia, _hora_a_minutos


class TestHorariosConflictan:
    """Tests for the time conflict detection function."""
    
    def test_same_time_same_day_conflicts(self):
        """Same time on same day should conflict."""
        assert _horarios_conflictan(
            "Lunes", "09:00", "11:00",
            "Lunes", "09:00", "11:00"
        ) == True
    
    def test_different_days_no_conflict(self):
        """Different days should not conflict."""
        assert _horarios_conflictan(
            "Lunes", "09:00", "11:00",
            "Martes", "09:00", "11:00"
        ) == False
    
    def test_adjacent_times_no_conflict(self):
        """Adjacent times (one ends when other starts) should not conflict."""
        assert _horarios_conflictan(
            "Lunes", "09:00", "11:00",
            "Lunes", "11:00", "13:00"
        ) == False
    
    def test_overlapping_times_conflict(self):
        """Overlapping times should conflict."""
        assert _horarios_conflictan(
            "Lunes", "09:00", "11:00",
            "Lunes", "10:00", "12:00"
        ) == True
    
    def test_contained_time_conflicts(self):
        """A time block contained in another should conflict."""
        assert _horarios_conflictan(
            "Lunes", "09:00", "13:00",
            "Lunes", "10:00", "11:00"
        ) == True
    
    def test_day_name_variants(self):
        """Different day name formats should still detect conflicts."""
        assert _horarios_conflictan(
            "Lunes", "09:00", "11:00",
            "lunes", "09:00", "11:00"
        ) == True
        
        assert _horarios_conflictan(
            "Miércoles", "09:00", "11:00",
            "miercoles", "09:00", "11:00"
        ) == True


class TestNormalizarDia:
    """Tests for day name normalization."""
    
    def test_normalize_lowercase(self):
        """Should normalize to lowercase."""
        assert _normalizar_dia("Lunes") == "lunes"
        assert _normalizar_dia("MARTES") == "martes"
    
    def test_normalize_accents(self):
        """Should handle accented characters."""
        assert _normalizar_dia("Miércoles") == "miercoles"
        assert _normalizar_dia("Sábado") == "sabado"
    
    def test_normalize_abbreviations(self):
        """Should handle common abbreviations."""
        assert _normalizar_dia("Lun") == "lunes"
        assert _normalizar_dia("Mar") == "martes"
        assert _normalizar_dia("Mie") == "miercoles"


class TestHoraAMinutos:
    """Tests for time to minutes conversion."""
    
    def test_midnight(self):
        """Midnight should be 0."""
        assert _hora_a_minutos("00:00") == 0
    
    def test_noon(self):
        """Noon should be 720."""
        assert _hora_a_minutos("12:00") == 720
    
    def test_afternoon(self):
        """14:30 should be 870."""
        assert _hora_a_minutos("14:30") == 870
    
    def test_end_of_day(self):
        """23:59 should be 1439."""
        assert _hora_a_minutos("23:59") == 1439
    
    def test_invalid_format_returns_zero(self):
        """Invalid format should return 0."""
        assert _hora_a_minutos("invalid") == 0
        assert _hora_a_minutos("") == 0
