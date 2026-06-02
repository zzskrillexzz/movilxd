"""
SearchBuilder — constructor de consultas de búsqueda con filtros y paginación.

Uso:
    sb = SearchBuilder(
        table='t_producto',
        search_fields=['pro_id', 'pro_nombre', 'pro_categoria'],
        exact_fields=['pro_estado', 'pro_categoria'],
        range_fields={'pro_precio': 'decimal', 'pro_fecha_caducidad': 'date'}
    )
    results = sb.execute(cursor, q='acetaminofen', pro_estado='Activo', page=1, limit=20)
    # → {'data': [...], 'total': 42, 'page': 1, 'limit': 20, 'pages': 3}
"""

from collections import OrderedDict


def _parse_value(value, field_type='string'):
    """Convierte un valor desde string al tipo adecuado para la DB."""
    if value is None or value == '':
        return None
    value = str(value).strip()
    if field_type == 'int':
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    if field_type == 'decimal':
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    if field_type == 'date':
        # Acepta YYYY-MM-DD o timestamp
        return value[:10]
    return value


class SearchBuilder:
    def __init__(self, table, search_fields=None, exact_fields=None, range_fields=None, join_clause=None, select_columns='*', default_order=None, allowed_extra_params=None):
        """
        table: nombre de la tabla principal (ej: 't_producto')
        search_fields: columnas donde buscar con LIKE (ej: ['pro_id', 'pro_nombre'])
        exact_fields: columnas para filtro exacto (ej: ['pro_estado', 'pro_categoria'])
        range_fields: columnas para filtro por rango, con tipo (ej: {'pro_precio': 'decimal', 'pro_fecha': 'date'})
        join_clause: cláusula JOIN adicional (opcional, ej: 'LEFT JOIN t_cliente ON ...')
        select_columns: qué seleccionar (ej: 'p.*, c.cli_nombre')
        default_order: orden por defecto (ej: 'pro_nombre ASC')
        allowed_extra_params: BUG-001 — lista de columnas permitidas como filtros extra (SQLi prevention)
        """
        self.table = table
        self.search_fields = search_fields or []
        self.exact_fields = exact_fields or []
        self.range_fields = range_fields or {}
        self.join_clause = join_clause or ''
        self.select_columns = select_columns
        self.default_order = default_order or '1 ASC'
        self.allowed_extra_params = allowed_extra_params or []  # BUG-001

    def _build_where(self, params):
        """Construye la cláusula WHERE y la tupla de valores."""
        conditions = []
        values = []

        # ── Búsqueda global (q) ──
        q = params.pop('q', None)
        if q and self.search_fields:
            like_conditions = []
            q_val = f'%{q}%'
            for field in self.search_fields:
                like_conditions.append(f'{field} LIKE %s')
                values.append(q_val)
            conditions.append(f'({ " OR ".join(like_conditions) })')

        # ── Filtros exactos ──
        for field in self.exact_fields:
            val = params.pop(field, None)
            if val is not None and str(val).strip():
                conditions.append(f'{field} = %s')
                values.append(_parse_value(val))

        # ── Filtros por rango ──
        for field, field_type in self.range_fields.items():
            val_from = params.pop(f'{field}_from', None)
            val_to = params.pop(f'{field}_to', None)
            if val_from is not None and str(val_from).strip():
                parsed = _parse_value(val_from, field_type)
                if parsed is not None:
                    conditions.append(f'{field} >= %s')
                    values.append(parsed)
            if val_to is not None and str(val_to).strip():
                parsed = _parse_value(val_to, field_type)
                if parsed is not None:
                    conditions.append(f'{field} <= %s')
                    values.append(parsed)

        # ── Parámetros extra (solo columnas autorizadas) ──
        # BUG-001: Validar contra whitelist para prevenir SQLi
        for key, val in params.items():
            if key.startswith('_') or key in ('page', 'limit', 'order_by', 'offset'):
                continue
            if val is not None and str(val).strip():
                # Si hay whitelist definida, solo permitir columnas listadas
                if self.allowed_extra_params and key not in self.allowed_extra_params:
                    continue  # Silenciosamente ignorar columnas no autorizadas
                conditions.append(f'{key} = %s')
                values.append(_parse_value(val))

        where_clause = ''
        if conditions:
            where_clause = 'WHERE ' + ' AND '.join(conditions)

        return where_clause, values

    def _sanitize_order_by(self, order_str):
        """
        BUG-001: Sanitiza ORDER BY para prevenir SQLi.
        Solo permite: identificador (columna) opcionalmente seguido de ASC/DESC.
        """
        if not order_str or not isinstance(order_str, str):
            return self.default_order
        order_str = order_str.strip()
        parts = order_str.split()
        column = parts[0]
        direction = parts[1].upper() if len(parts) > 1 else 'ASC'
        # Validar que el nombre de columna solo contenga caracteres permitidos
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', column):
            return self.default_order
        if direction not in ('ASC', 'DESC'):
            direction = 'ASC'
        return f'{column} {direction}'

    def execute(self, cursor, page=1, limit=50, order_by=None, **filters):
        """
        Ejecuta la consulta con filtros y paginación.
        Retorna: {'data': [...], 'total': N, 'page': N, 'limit': N, 'pages': N}
        """
        page = max(1, int(page))
        limit = max(1, min(100, int(limit)))
        offset = (page - 1) * limit
        order = order_by or self.default_order

        where_clause, values = self._build_where(filters)

        # ── Total de registros ──
        count_sql = f'SELECT COUNT(*) FROM {self.table} {self.join_clause} {where_clause}'
        cursor.execute(count_sql, values)
        total = cursor.fetchone()[0]

        # ── Datos paginados ──
        # BUG-001: Sanitizar order_by para prevenir SQLi
        _order_sanitized = self._sanitize_order_by(order)
        data_sql = (
            f'SELECT {self.select_columns} '
            f'FROM {self.table} {self.join_clause} {where_clause} '
            f'ORDER BY {_order_sanitized} LIMIT %s OFFSET %s'
        )
        cursor.execute(data_sql, values + [limit, offset])
        rows = cursor.fetchall()

        # Obtener nombres de columnas
        col_names = [desc[0] for desc in cursor.description]

        data = []
        for row in rows:
            item = OrderedDict()
            for i, col in enumerate(col_names):
                val = row[i]
                # Convertir bytes a string para JSON
                if isinstance(val, bytes):
                    val = val.decode('utf-8', errors='replace')
                item[col] = val
            data.append(item)

        pages = max(1, -(-total // limit))  # ceil division

        return {
            'data': data,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': pages
        }
