# Arquitectura y decisiones

## Contexto

Sistema de agenda orientado a demostrar un flujo cloud completo y reproducible sin convertir una carga pequeña en microservicios prematuros. El monolito modular reduce costo operativo; ECS permite separar servicios cuando las métricas lo justifiquen.

## Recorrido de una solicitud

1. CloudFront termina HTTPS y entrega los assets privados desde S3 mediante OAC.
2. Los comportamientos `/turnos*`, `/auth*`, `/health` y `/ready` encaminan la API hacia el ALB, evitando mixed content y CORS en producción.
3. El ALB comprueba `/health` y solo alcanza tareas Fargate a través de security groups.
4. ECS obtiene la contraseña administrada desde Secrets Manager y conecta con RDS privado.
5. CloudWatch recibe logs con request ID y latencia; una alarma vigila targets no saludables.

## Decisiones y trade-offs

| Decisión | Motivo | Trade-off |
| --- | --- | --- |
| Monolito FastAPI | Dominio pequeño, despliegue simple | Se modularizará antes de sumar nuevos contextos |
| ECS Fargate | Sin gestión de servidores y escalado horizontal | Mayor costo base que Lambda para tráfico esporádico |
| RDS PostgreSQL | Integridad y consultas transaccionales | Requiere migraciones y capacidad mínima permanente |
| CloudFront como único origen público | HTTPS y API sin CORS/mixed content | Se deben declarar explícitamente rutas dinámicas |
| Cancelación lógica | Preserva auditoría funcional | La tabla crece y exige política de retención |

## Integridad y concurrencia

La API hace una comprobación rápida de disponibilidad y PostgreSQL la garantiza con el índice único parcial `uq_turnos_fecha_pendiente`. Si dos tareas reservan simultáneamente, una confirma y la otra traduce la violación de integridad a `409 Conflict`.

## Despliegue y rollback

CI valida backend, frontend y Terraform antes de desplegar. Cada imagen recibe el SHA del commit, se registra una nueva revisión de task definition y ECS espera estabilidad con circuit breaker y rollback automático. El frontend se publica después y un smoke test verifica el health check a través de CloudFront.

Las migraciones se ejecutan al iniciar el contenedor. Esto es aceptable con una sola tarea; al escalar, deben pasar a un job único previo al despliegue y seguir la estrategia expand/contract.

## Modelo de amenazas resumido

- **Exposición de datos:** RDS no es público y solo acepta el security group de ECS.
- **Robo de credenciales:** RDS administra su secreto; GitHub usa tokens OIDC temporales.
- **Acceso directo a objetos:** S3 bloquea acceso público y limita lectura a CloudFront.
- **Acceso no autorizado:** las rutas de negocio requieren un token firmado y producción obtiene las claves desde Secrets Manager; Cognito, WAF y rate limiting son la siguiente evolución para clientes externos.
- **Diagnóstico:** `X-Request-ID`, logs de duración y health checks reducen el tiempo de investigación.

## SLO propuesto

- Disponibilidad mensual: 99.5%.
- p95 de lectura: menor a 500 ms.
- Tasa de respuestas 5xx: menor a 1%.
- Recovery Time Objective: 60 minutos; Recovery Point Objective: 24 horas.

Estos objetivos son una propuesta y deben validarse con tráfico real, dashboards y pruebas de recuperación.
