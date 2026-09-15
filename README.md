# Sistema de Turnos en AWS

Aplicación full stack para crear, consultar y cancelar turnos, diseñada como demostración de una arquitectura cloud reproducible. Combina React, FastAPI, PostgreSQL y una infraestructura administrada con Terraform sobre AWS.

## Arquitectura

```mermaid
flowchart LR
    U[Usuario] --> CF[CloudFront]
    CF --> S3[S3 - React]
    U --> ALB[Application Load Balancer]
    ALB --> ECS[ECS Fargate - FastAPI]
    ECS --> RDS[(RDS PostgreSQL)]
    ECS --> CW[CloudWatch Logs]
    GHA[GitHub Actions] --> ECR[ECR]
    ECR --> ECS
    GHA --> S3
```

La base de datos no es pública y solo acepta tráfico desde el backend. RDS administra la contraseña maestra en Secrets Manager y ECS la inyecta sin guardarla en el repositorio.

## Tecnologías

- **Frontend:** React 19, Vite y Axios.
- **Backend:** Python 3.12, FastAPI, SQLAlchemy y Pydantic.
- **Datos:** PostgreSQL en Amazon RDS.
- **Cloud:** ECS Fargate, ECR, ALB, S3, CloudFront y CloudWatch.
- **DevOps:** Docker, Terraform y GitHub Actions.

## Funcionalidades

- Crear turnos futuros con validación de cliente, servicio y disponibilidad.
- Buscar y filtrar turnos con paginación desde la API.
- Cancelar un turno sin borrar su historial.
- Reprogramar turnos activos y prevenir reservas simultáneas para el mismo horario.
- Health check para el balanceador y documentación OpenAPI en `/docs`.
- Interfaz adaptable a escritorio y dispositivos móviles.

## Ejecución local

### Backend

```bash
cd SistemaTurnosAWS/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

La configuración de ejemplo utiliza SQLite para evaluar el proyecto sin PostgreSQL.

### Frontend

En otra terminal:

```bash
cd SistemaTurnosAWS/frontend
cp .env.example .env
npm ci
npm run dev
```

Abre `http://localhost:5173`. La API y su documentación quedan disponibles en `http://localhost:8000` y `http://localhost:8000/docs`.

## Variables de entorno

| Componente | Variable | Descripción |
| --- | --- | --- |
| Backend | `DATABASE_URL` | URL completa para desarrollo local. |
| Backend | `CORS_ORIGINS` | Orígenes permitidos separados por comas. |
| Backend | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Configuración usada en ECS. |
| Frontend | `VITE_API_URL` | URL pública de FastAPI. |

Nunca confirmes archivos `.env`, credenciales de AWS, archivos `tfvars` ni estados de Terraform.

## Pruebas y controles

```bash
cd SistemaTurnosAWS/backend && pytest
cd SistemaTurnosAWS/frontend && npm run lint && npm run build
terraform -chdir=SistemaTurnosAWS/terraform fmt -check -recursive
terraform -chdir=SistemaTurnosAWS/terraform validate
```

El pipeline exige al menos 85% de cobertura del backend y ejecuta estos controles antes de permitir el despliegue.

## Infraestructura y despliegue

1. Autentícate en AWS, define `cors_origins` con la URL real de CloudFront y ejecuta `terraform init`, `terraform plan` y `terraform apply` dentro de `SistemaTurnosAWS/terraform`.
2. Configura GitHub OIDC y los secrets `AWS_DEPLOY_ROLE_ARN`, `S3_BUCKET` y `CLOUDFRONT_DISTRIBUTION_ID`. No se almacenan access keys permanentes.
3. Un push a `main` valida el proyecto, publica la imagen Docker y actualiza frontend y backend.

> La infraestructura genera costos. Al terminar una demostración, ejecuta `terraform destroy` y comprueba que no queden recursos activos.

## Decisiones de seguridad

- RDS permanece sin acceso público y utiliza almacenamiento cifrado.
- El backend solo acepta tráfico proveniente del ALB.
- S3 bloquea el acceso público y CloudFront utiliza Origin Access Control.
- GitHub Actions asume un rol temporal mediante OIDC, sin access keys permanentes.
- Secrets Manager entrega la contraseña de base de datos directamente a ECS.
- CloudFront publica frontend y API bajo HTTPS en el mismo origen, evitando mixed content.
- ECS escala automáticamente entre una y cuatro tareas según CPU y CloudWatch detecta targets no saludables.

## Señales de calidad

- Migraciones versionadas con Alembic, ejecutadas antes de iniciar la API.
- Contratos HTTP probados de extremo a extremo con `TestClient` y cobertura mínima en CI.
- Respuestas paginadas, filtros, búsqueda, conflictos `409` y validación de fechas futuras.
- Request ID propagado en cada respuesta y logs con latencia para facilitar el diagnóstico.
- Imagen Docker trazable mediante la etiqueta SHA del commit.

Consulta [Arquitectura y decisiones](docs/ARCHITECTURE.md) para conocer los trade-offs, el modelo de amenazas y la estrategia de evolución.

## Próximos pasos

- Añadir autenticación federada con Amazon Cognito y roles de usuario.
- Añadir notificaciones de alarmas mediante SNS y métricas de negocio.
- Separar ambientes y almacenar el estado de Terraform en S3 con locking.

## Licencia

Distribuido bajo la [Licencia MIT](LICENSE).
