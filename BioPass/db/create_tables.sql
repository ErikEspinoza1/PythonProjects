-- Script de creación de la tabla de usuarios
-- Soporta almacenamiento de imágenes binarias (BYTEA)

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    foto_bytes BYTEA NOT NULL,  -- Foto original completa
    cara_bytes BYTEA NOT NULL,  -- Recorte de la cara (para entrenamiento)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);