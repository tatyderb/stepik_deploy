from dataclasses import dataclass

@dataclass
class Settings:
    """Настройка разделителя шага"""
    LEGACY_STEP_BEGIN: str = "##"

    STEP_BEGIN: str = LEGACY_STEP_BEGIN # По умолчанию '##' - стандартный заголовок второго уровня
    # Использование:
    # from setting import settings
    
    #if settings.STEP_BEGIN ...."""

settings = Settings()