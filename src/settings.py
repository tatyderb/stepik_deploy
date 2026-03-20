from dataclasses import dataclass

@dataclass
class Settings:
    """Настройка разделителя шага"""
    
    STEP_BEGIN: str = '##' # По умолчанию '##' - стандартный заголовок второго уровня
    # Использование:
    # from setting import settings
    
    #if settings.STEP_BEGIN ...."""

settings = Settings()