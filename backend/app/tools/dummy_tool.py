from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class DummyInput(BaseModel):
    """Input para la herramienta dummy"""
    student_id: str = Field(description="ID del estudiante")


class DummyTool(BaseTool):
    name = "dummy_academic_selector"
    description = """Herramienta de prueba que simula consultar 
    materias elegibles para un estudiante."""
    args_schema: Type[BaseModel] = DummyInput
    
    def _run(self, student_id: str) -> str:
        """Ejecutar la herramienta"""
        # Por ahora solo retorna datos fake
        return f"Estudiante {student_id} puede cursar: Cálculo II, Programación Web, Bases de Datos"
    
    async def _arun(self, student_id: str) -> str:
        """Versión asíncrona"""
        return self._run(student_id)