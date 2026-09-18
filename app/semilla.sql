-- Datos minimos para probar el sistema y ver la cola de cocina, la
-- vista de mesero, la cuenta de una mesa y un reporte de faltante
-- funcionando de punta a punta.

INSERT INTO mesa (id, nombre) VALUES
    (1, 'Mesa 1'),
    (2, 'Mesa 2'),
    (3, 'Mesa 3');

INSERT INTO mesero (id, nombre) VALUES
    (1, 'Ana'),
    (2, 'Luis');

INSERT INTO plato (id, nombre, precio) VALUES
    (1, 'Hamburguesa clasica',   25000),
    (2, 'Pizza margarita',       32000),
    (3, 'Ensalada cesar',        18000),
    (4, 'Pasta alfredo',         27000),
    (5, 'Limonada natural',       8000),
    (6, 'Brownie con helado',    12000);

INSERT INTO ingrediente (id, nombre, disponible) VALUES
    (1,  'pan',                1),
    (2,  'carne_de_res',       1),
    (3,  'queso',              1),
    (4,  'lechuga',            1),
    (5,  'tomate',             1),
    (6,  'masa_de_pizza',      1),
    (7,  'salsa_de_tomate',    1),
    (8,  'mozzarella',         1),
    -- Ingrediente agotado: deja sin ofrecer la ensalada cesar (receta
    -- mas abajo), que es la unica que lo usa.
    (9,  'pollo',              0),
    (10, 'aderezo_cesar',      1),
    (11, 'crutones',           1),
    (12, 'pasta',              1),
    (13, 'crema_de_leche',     1),
    (14, 'limon',              1),
    (15, 'azucar',             1),
    (16, 'agua',               1),
    (17, 'chocolate',          1),
    (18, 'helado_de_vainilla', 1);

INSERT INTO plato_ingrediente (plato_id, ingrediente_id) VALUES
    -- Hamburguesa clasica
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
    -- Pizza margarita
    (2, 6), (2, 7), (2, 8),
    -- Ensalada cesar: depende de pollo (id 9), que esta agotado.
    (3, 4), (3, 9), (3, 10), (3, 11),
    -- Pasta alfredo
    (4, 12), (4, 13), (4, 3),
    -- Limonada natural
    (5, 14), (5, 15), (5, 16),
    -- Brownie con helado
    (6, 17), (6, 18);

-- Pedido 1, mesa 1, tomado por Ana: un item recien pedido (PENDIENTE) y
-- otro que cocina ya empezo (EN_PREPARACION), para ver la cola con dos
-- items en dos estados distintos y su orden por antiguedad.
INSERT INTO pedido (id, mesa_id, mesero_id, creado_en) VALUES
    (1, 1, 1, '2026-09-18T12:00:00.000Z');

INSERT INTO item_pedido (id, pedido_id, plato_id, precio_congelado, estado, creado_en, iniciado_en) VALUES
    (1, 1, 1, 25000, 'PENDIENTE',      '2026-09-18T12:00:00.000Z', NULL),
    (2, 1, 2, 32000, 'EN_PREPARACION', '2026-09-18T12:00:30.000Z', '2026-09-18T12:05:00.000Z');

-- Un tercer item del mismo pedido que cocina cancelo porque, al ir a
-- prepararlo, encontro que faltaba pollo. Genera el reporte de
-- faltante que el administrador debe atender.
INSERT INTO item_pedido (id, pedido_id, plato_id, precio_congelado, estado, creado_en, cancelado_en) VALUES
    (3, 1, 3, 18000, 'CANCELADO', '2026-09-18T12:01:00.000Z', '2026-09-18T12:04:00.000Z');

INSERT INTO reporte_faltante (id, ingrediente_id, item_pedido_id, nota, creado_en) VALUES
    (1, 9, 3, 'Se agoto el pollo, se cancelo la ensalada cesar del pedido 1.', '2026-09-18T12:04:00.000Z');

-- Pedido 2, mesa 2, tomado por Luis: un item listo para entregar (para
-- ver la vista de Luis) y uno ya entregado. Ningun item esta cancelado
-- y uno sigue sin entregar, asi que esta mesa a proposito no tiene
-- pagos todavia (A-19 de ASSUMPTIONS.md: no se aceptan pagos mientras
-- queden items no cancelados sin entregar).
INSERT INTO pedido (id, mesa_id, mesero_id, creado_en) VALUES
    (2, 2, 2, '2026-09-18T12:10:00.000Z');

INSERT INTO item_pedido (id, pedido_id, plato_id, precio_congelado, estado, creado_en, iniciado_en, listo_en) VALUES
    (4, 2, 5, 8000, 'LISTO', '2026-09-18T12:10:00.000Z', '2026-09-18T12:11:00.000Z', '2026-09-18T12:13:00.000Z');

INSERT INTO item_pedido (id, pedido_id, plato_id, precio_congelado, estado, creado_en, iniciado_en, listo_en, entregado_en) VALUES
    (5, 2, 6, 12000, 'ENTREGADO', '2026-09-18T12:10:10.000Z', '2026-09-18T12:11:10.000Z', '2026-09-18T12:14:00.000Z', '2026-09-18T12:16:00.000Z');

-- Pedido 3, mesa 3, tomado por Ana: todos sus items ya entregados, asi
-- que la mesa si puede recibir pagos. Sirve para probar la consulta de
-- total y saldo de la cuenta.
INSERT INTO pedido (id, mesa_id, mesero_id, creado_en) VALUES
    (3, 3, 1, '2026-09-18T11:30:00.000Z');

INSERT INTO item_pedido (id, pedido_id, plato_id, precio_congelado, estado, creado_en, iniciado_en, listo_en, entregado_en) VALUES
    (6, 3, 4, 27000, 'ENTREGADO', '2026-09-18T11:30:00.000Z', '2026-09-18T11:32:00.000Z', '2026-09-18T11:40:00.000Z', '2026-09-18T11:42:00.000Z'),
    (7, 3, 5,  8000, 'ENTREGADO', '2026-09-18T11:30:10.000Z', '2026-09-18T11:32:10.000Z', '2026-09-18T11:35:00.000Z', '2026-09-18T11:42:30.000Z');

-- Un pago parcial sobre la mesa 3: el total de sus items no cancelados
-- es 27000 + 8000 = 35000; este pago deja un saldo pendiente de 15000,
-- calculado por consulta, no guardado.
INSERT INTO pago (id, mesa_id, monto, propina, medio, pagador, creado_en) VALUES
    (1, 3, 20000, 2000, 'EFECTIVO', 'cliente mesa 3', '2026-09-18T12:20:00.000Z');
