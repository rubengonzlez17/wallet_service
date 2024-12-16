# QUESTIONS

### 1. **¿Cómo optimizar el rendimiento del servicio de listado de operaciones?**

- **Paginación y límites:** Implementar paginación y limitar el número de resultados por página para reducir la carga en el servidor y la transferencia de datos.
- **Filtros específicos:** Permitir filtrar operaciones por fechas, tipos o estados, para evitar la recuperación de datos innecesarios.
- **Índices en la base de datos:** Asegurarse de que las columnas más consultadas (como `wallet_id`, `created_at`) estén indexadas.
- **Consultas optimizadas:** Usar `select_related` y `prefetch_related` en Django para reducir las consultas N+1 en relaciones entre modelos.
- **Caching:** Cachear las respuestas más frecuentes usando Redis o herramientas similares, especialmente para operaciones históricas que no cambian.

---

### 2. Qué alternativas planteas en el caso que la base de datos relacional de la aplicación se convierta en un cuello de botella por saturación en las operaciones de lectura? ¿Y para las de escritura?

### **Lecturas:**

- **Replica-read pattern:** Usar réplicas de solo lectura para distribuir la carga de lecturas.
- **Caching:** Implementar caché en capas intermedias (por ejemplo: Redis) para datos de lectura frecuente.
- **Materialized views:** Usar vistas materializadas para precomputar resultados frecuentes. Podriamos generar una vista donde se relacionen los usuarios y sus wallets, de tal forma que nos podriamos ahorrar una consulta a la base de datos cada vez que queremos ver el estado de nuestras wallets.

### **Escrituras:**

- **Cola de tareas:** Desacoplar las escrituras intensivas usando colas (por ejemplo, RabbitMQ, Celery) para procesar datos en segundo plano.

---

### 3. Dicen que las bases de datos relacionales no escalan bien, se me ocurre montar el proyecto con alguna NoSQL, ¿qué me recomiendas?

Depende del caso de uso:

- **Relacional:** Sigue siendo ideal si necesitas transacciones ACID y relaciones complejas, como entre usuarios, wallets y transacciones. Usa optimizaciones antes de descartar.
- **NoSQL (ej., MongoDB):** Es útil si la carga es altamente no estructurada, la lectura/escritura es masiva, y puedes sacrificar consistencia en favor de velocidad y escalabilidad horizontal. Pero en este caso, hasta lo que vemos en el enunciado, los datos estan altamente estructurados, por lo que **descartaria esta opción**.
- **Modelo híbrido:** Puedes usar un enfoque combinado (ej., PostgreSQL + Redis para caché, o DynamoDB para eventos históricos). **Me inclinaria por esta opción.**

---

### 5. **Métricas y servicios para comprobar el funcionamiento**

- **Métricas principales:**
    - **Latencia:** Tiempos de respuesta de la API.
    - **Errores:** Tasa de errores HTTP (500, 400, 403, 404).
    - **Disponibilidad:** Tiempo de actividad del servidor.
    - **Uso de recursos:** CPU, memoria, y conexiones activas en la base de datos.
- **Herramientas recomendadas:**
    - **APM (Application Performance Monitoring):** New Relic o Datadog para rastrear errores y rendimiento.
    - **Logging:** Usar herramientas como SPLUNK o KIBANA para analizar logs.
    - **Health checks:** Implementar un endpoint `/health` que confirme que el servicio esta funcionando.
    - **Alerting:** Configurar alertas automáticas basadas en umbrales de rendimiento con Prometheus o CloudWatch.
- **Test periodicos:** Además de lanzar tests en cada Pull Request y en cada merge con la rama principal, una vez el servicio este desplegado, una buena practica seria lanzar tests periodicos para cerciorarnos de que todo esta funcionando según lo previsto.
