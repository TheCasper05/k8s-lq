"""Módulo de autenticación para endpoints de la API."""

from fastapi import Header, HTTPException, status


async def verify_token(api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    Verifica el token de API proporcionado en el header.

    Args:
        api_key: API key proporcionada en el header X-API-Key

    Returns:
        El API key si es válido

    Raises:
        HTTPException: Si el API key no es válido o no se proporciona
    """
    from src.config import settings

    # Verificar que el API key coincida con el configurado
    # En producción, esto debería ser un token separado
    expected_key = settings.api_key

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key no configurada en el servidor",
        )

    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o no proporcionada",
            headers={"WWW-Authenticate": "X-API-Key"},
        )

    return api_key
