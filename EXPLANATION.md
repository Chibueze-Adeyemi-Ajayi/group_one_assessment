# Architecture & Design: Centralized License Service

## 1. Problem Statement
**group.one** requires a unified "Source of Truth" for license management. The challenge is to support multiple independent brands (WP Rocket, RankMath, etc.) while allowing them to provision licenses that end-user products can validate. The system must be:
- **Multi-tenant**: Secure separation between brands.
- **Key-centric**: A single license key can authorize multiple product entitlements.
- **Scalable**: Optimized for millions of activation checks.

## 2. Technical Architecture
The service follows a monolithic architecture with a modular internal structure, chosen for rapid development and ease of consistency in this core assessment phase.

### Core Entities (Data Model)
- **Brand**: The top-level tenant (e.g., RankMath).
- **Product**: Belonging to a Brand (e.g., Content AI).
- **LicenseKey**: The unique string provided to the user.
- **License**: An entitlement for a specific Product, linked to a LicenseKey.
- **Activation**: A specific instance (site URL/machine ID) using a License seat.

### Administrative Flow
1. **Admin** creates a **Brand** via `POST /api/brands/`.
2. **Admin** creates **Products** for that brand via `POST /api/products/`.

### Provisioning Flow (US1)
1. **Brand A** calls `POST /api/provision/` with customer email and product/brand slugs.
2. System generates **LicenseKey #1**.
3. System creates **License #1** (Product: WP Rocket, Key: #1).
4. **Brand A** can call `POST /api/provision/` again with the same email and a different product slug to add entitlements to the same key.

## 3. Implementation vs. Design Decisions

| Feature | Status | Decision/Trade-off |
| :--- | :--- | :--- |
| **Multi-tenancy** | Implemented | Used ForeignKeys to `Brand` and implemented permission checks in DRF views to ensure brands only see their own data. |
| **Seat Management** | Designed | Modeled `Activation` table with `instance_id`. The logic checks `total_seats` on `License` before allowing a new `Activation`. |
| **JWT Auth** | Implemented | Chosen for statelessness, allowing the service to scale horizontally without session synchronization. |
| **Caching** | Designed | In a production scenario, Redis would cache `is_valid` status for LicenseKeys to reduce DB load on frequent check calls. |

## 4. Scalability & Resilience
### Multi-regional Deployment
To support global WordPress users, the API should be deployed behind a Global Load Balancer with read-replicas in major regions (US, EU, Asia) to minimize latency for license checks.

### High Availability
- **Database**: PostgreSQL with Hot Standby.
- **API**: Horizontal scaling using Kubernetes (autoscale based on CPU/Request count).

## 5. Observability
- **Logging**: Structured JSON logging for all provision/activation events.
- **Monitoring**: Prometheus metrics for request latency and license failure rates.
- **Tracing**: OpenTelemetry (Signoz/Jaeger) to trace requests from Brand systems through the License Service.

## 6. Security
- **Internal APIs (Brands)**: Protected via OAuth2/Client Credentials or JWT with Brand-specific scopes.
- **External APIs (Products)**: Rate-limited key validation to prevent brute-force attacks.
- **Database**: Encryption at rest and sensitive data (emails) can be hashed/encrypted if GDPR requirements mandate.

## 7. How to Run Locally
*See [README.md](./README.md) for step-by-step setup instructions.*
