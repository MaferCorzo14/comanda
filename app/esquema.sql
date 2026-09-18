-- Esquema de datos del sistema de comanda.
--
-- SQLite no aplica las claves foraneas salvo que la conexion ejecute
-- PRAGMA foreign_keys = ON. Aqui se escriben igual, como documentacion
-- y para que el planificador de consultas las use, pero la activacion
-- real ocurre despues en db.py.

-- Mesa fisica del restaurante. Ancla la cuenta y los pedidos.
CREATE TABLE mesa (
    id     INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);

-- Persona que atiende mesas: registra pedidos y queda asignada a ellos.
CREATE TABLE mesero (
    id     INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);

-- Plato del menu. El precio aqui es el precio vigente; el precio ya
-- cobrado en un pedido se congela aparte en item_pedido.precio_congelado.
CREATE TABLE plato (
    id     INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio INTEGER NOT NULL CHECK (precio > 0)
);

-- Ingrediente que puede formar parte de una receta. La disponibilidad
-- es un hecho de entrada (la administra el administrador), no un valor
-- derivado, por eso se guarda como columna.
CREATE TABLE ingrediente (
    id         INTEGER PRIMARY KEY,
    nombre     TEXT NOT NULL,
    disponible INTEGER NOT NULL DEFAULT 1 CHECK (disponible IN (0, 1))
);

-- Receta: que ingredientes lleva cada plato. La disponibilidad de un
-- plato (regla 2 de AGENTS.md) NO se guarda en ninguna tabla: se deriva
-- consultando esta tabla junto con ingrediente.disponible. Un plato se
-- ofrece solo si tiene al menos una fila aqui y todos sus ingredientes
-- estan disponibles.
CREATE TABLE plato_ingrediente (
    plato_id      INTEGER NOT NULL REFERENCES plato(id),
    ingrediente_id INTEGER NOT NULL REFERENCES ingrediente(id),
    -- La clave primaria compuesta es lo que impide que el mismo
    -- ingrediente aparezca dos veces en la receta de un mismo plato.
    PRIMARY KEY (plato_id, ingrediente_id)
);

-- Pedido: una ronda de items pedidos junto para una mesa, tomada por un
-- mesero. No se le agregan items despues de creado (ver AGENTS.md); una
-- ronda nueva es un pedido nuevo. El estado del pedido NO se guarda:
-- se deriva de los estados de sus items (completo si todos estan en
-- LISTO o CANCELADO, anulado si todos estan en CANCELADO).
CREATE TABLE pedido (
    id         INTEGER PRIMARY KEY,
    mesa_id    INTEGER NOT NULL REFERENCES mesa(id),
    mesero_id  INTEGER NOT NULL REFERENCES mesero(id),
    creado_en  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Item de pedido: una unidad de un plato dentro de un pedido. Pedir tres
-- hamburguesas crea tres filas, porque cada item avanza por su propio
-- ciclo de estados (regla 1 de AGENTS.md).
--
-- El precio se congela en precio_congelado al momento de crear el item:
-- un cambio posterior en plato.precio no altera items ya pedidos.
--
-- Cada transicion de estado queda registrada en su propia columna de
-- marca de tiempo (creado_en cubre la entrada a PENDIENTE). El orden de
-- las transiciones (sin saltos, sin retroceso, CANCELADO solo desde
-- PENDIENTE) no se puede expresar como una restriccion estatica de
-- esquema porque depende del valor anterior de la fila: se aplica en la
-- aplicacion con una sola sentencia UPDATE condicionada al estado previo
-- (ver ADR-003), no leyendo y despues escribiendo.
CREATE TABLE item_pedido (
    id               INTEGER PRIMARY KEY,
    pedido_id        INTEGER NOT NULL REFERENCES pedido(id),
    plato_id         INTEGER NOT NULL REFERENCES plato(id),
    precio_congelado INTEGER NOT NULL CHECK (precio_congelado > 0),
    nota             TEXT,
    -- Unico lugar que restringe los valores validos del estado. Un
    -- valor fuera de esta lista es rechazado por la base de datos.
    estado           TEXT NOT NULL DEFAULT 'PENDIENTE'
                     CHECK (estado IN ('PENDIENTE', 'EN_PREPARACION', 'LISTO', 'ENTREGADO', 'CANCELADO')),
    creado_en        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    iniciado_en      TEXT,
    listo_en         TEXT,
    entregado_en     TEXT,
    cancelado_en     TEXT
);

-- Pago parcial de la cuenta de una mesa. El total de la cuenta y el
-- saldo pendiente NO se guardan: se derivan sumando precio_congelado de
-- los items no cancelados (total) y restando la suma de pagos.monto
-- (saldo). La propina se guarda aparte porque si se sumara al monto
-- podria hacer que los pagos superen el total de la cuenta.
CREATE TABLE pago (
    id        INTEGER PRIMARY KEY,
    mesa_id   INTEGER NOT NULL REFERENCES mesa(id),
    monto     INTEGER NOT NULL CHECK (monto > 0),
    propina   INTEGER NOT NULL DEFAULT 0 CHECK (propina >= 0),
    medio     TEXT NOT NULL CHECK (medio IN ('EFECTIVO', 'TARJETA')),
    pagador   TEXT,
    creado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Reporte de un ingrediente faltante, hecho por cocina cuando cancela un
-- item por falta de un ingrediente (ver ASSUMPTIONS.md A-12). Queda
-- pendiente de atencion del administrador hasta que atendido_en se
-- llena. item_pedido_id es opcional porque un reporte tambien puede
-- surgir sin que haya un item concreto cancelado en ese momento.
CREATE TABLE reporte_faltante (
    id             INTEGER PRIMARY KEY,
    ingrediente_id INTEGER NOT NULL REFERENCES ingrediente(id),
    item_pedido_id INTEGER REFERENCES item_pedido(id),
    nota           TEXT,
    creado_en      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    atendido_en    TEXT
);

-- Indices: uno por cada consulta obligatoria. No hay indices que
-- ninguna consulta use.

-- Cola de cocina: items en PENDIENTE o EN_PREPARACION, ordenados
-- estrictamente por antiguedad (creado_en). Indice parcial: solo cubre
-- las filas que la cola necesita y ya quedan en el orden que la
-- consulta pide, así que la consulta es un recorrido secuencial del
-- indice sin ordenar aparte.
CREATE INDEX idx_item_pedido_cola
    ON item_pedido (creado_en)
    WHERE estado IN ('PENDIENTE', 'EN_PREPARACION');

-- Vista del mesero: items en LISTO de los pedidos de un mesero.
-- idx_pedido_mesero resuelve "pedidos de este mesero"; el indice
-- parcial sobre item_pedido resuelve "sus items en LISTO" sin escanear
-- items en otros estados.
CREATE INDEX idx_pedido_mesero
    ON pedido (mesero_id);

CREATE INDEX idx_item_pedido_listo
    ON item_pedido (pedido_id)
    WHERE estado = 'LISTO';

-- Total y saldo de la cuenta de una mesa: se suman los precios
-- congelados de los items no cancelados de todos los pedidos de la
-- mesa, y se resta la suma de sus pagos. idx_pedido_mesa resuelve "los
-- pedidos de esta mesa"; el indice parcial sobre item_pedido resuelve
-- "sus items no cancelados" sin escanear los cancelados; idx_pago_mesa
-- resuelve la suma de pagos de la mesa.
CREATE INDEX idx_pedido_mesa
    ON pedido (mesa_id);

CREATE INDEX idx_item_pedido_no_cancelado
    ON item_pedido (pedido_id)
    WHERE estado != 'CANCELADO';

CREATE INDEX idx_pago_mesa
    ON pago (mesa_id);
