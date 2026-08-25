DROP DATABASE IF EXISTS montessori;
CREATE DATABASE montessori CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE montessori;

CREATE TABLE usuarios(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(100) NULL,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(30) NOT NULL DEFAULT 'Administrador',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO usuarios(nombre, usuario, correo, password, rol)
VALUES(
    'Administrador',
    'admin',
    'admin@montessori.com',
    'scrypt:32768:8:1$uH3yX9mZ$123456', 
    'Administrador'
);

CREATE TABLE categorias(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

INSERT INTO categorias(nombre)
VALUES
    ('Salas'),
    ('Comedores'),
    ('Base Camas'),
    ('Colchones');

CREATE TABLE productos(
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    categoria_id INT NOT NULL,
    material VARCHAR(80),
    color VARCHAR(50),
    largo DECIMAL(6,2) DEFAULT 0.00,
    ancho DECIMAL(6,2) DEFAULT 0.00,
    alto DECIMAL(6,2) DEFAULT 0.00,
    precio DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    descripcion TEXT,
    imagen VARCHAR(255),

    FOREIGN KEY(categoria_id)
        REFERENCES categorias(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE clientes(
    id INT AUTO_INCREMENT PRIMARY KEY,
    telefono VARCHAR(20),
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100),
    direccion VARCHAR(150)
) ENGINE=InnoDB;

CREATE TABLE proveedores(
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    direccion VARCHAR(150)
) ENGINE=InnoDB;

CREATE TABLE ventas(
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    FOREIGN KEY(cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE detalle_ventas(
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    FOREIGN KEY(venta_id)
        REFERENCES ventas(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY(producto_id)
        REFERENCES productos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;