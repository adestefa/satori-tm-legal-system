# TM Dockerization & Multi-Tenant Deployment Plan

## Phase 1: System Analysis & Preparation (Days 1-2)
**Objective:** Analyze current system and prepare for containerization

### 1.1 Configuration Audit
- Map all hardcoded paths and configurations across all four services
- Identify environment-specific settings requiring parameterization
- Document current dependency requirements and service interactions

### 1.2 Multi-Tenant Configuration Design
- Create JSON schema for client-specific configurations
- Design template structure for firm branding (masthead, login screen, settings)
- Plan data isolation strategy for multi-tenant file storage

### 1.3 Backup Strategy
- Create comprehensive backup using `scripts/backup.sh` before containerization
- Establish rollback procedures for each development phase

## Phase 2: Containerization Architecture (Days 3-5)
**Objective:** Create Docker containers for all TM services

### 2.1 Base Image Creation
- Design multi-stage Dockerfile for Python services (Tiger, Monkey, Dashboard)
- Create Node.js Dockerfile for Browser service
- Implement shared base image for consistency

### 2.2 Service-Specific Containers
- **Tiger Service**: Containerize ML document processing with volume mounts
- **Monkey Service**: Containerize template engine with template volume
- **Dashboard Service**: Containerize web interface with configuration injection
- **Browser Service**: Containerize PDF generation with Chromium dependencies

### 2.3 Docker Compose Configuration
- Create `docker-compose.yml` with service definitions
- Configure networking between services
- Design volume strategy for persistent data and configuration

## Phase 3: Configuration System (Days 6-7)
**Objective:** Implement JSON-driven multi-tenant configuration

### 3.1 Configuration Schema
- Create comprehensive JSON schema for client configurations
- Include firm details, branding, authentication, and service settings
- Design validation system for configuration integrity

### 3.2 Environment Variable Injection
- Map JSON configuration to environment variables
- Implement configuration loading in each service
- Create configuration validation and error handling

### 3.3 Template System
- Design branded template system for client customization
- Create configuration-driven UI elements (masthead, login, settings)
- Implement theme and branding injection

## Phase 4: Coolify Integration (Days 8-10)
**Objective:** Prepare for Coolify deployment

### 4.1 Coolify Documentation Research
- Create comprehensive Coolify setup documentation in `/TM/coolify/`
- Document API endpoints and deployment automation
- Design multi-tenant deployment workflow

### 4.2 Deployment Automation
- Create FastAPI provisioning service for client onboarding
- Design web form for client configuration generation
- Implement Coolify API integration for automated deployment

### 4.3 Resource Management
- Design resource allocation strategy for multi-tenant Linode deployment
- Plan scaling and monitoring for shoulder-to-shoulder deployment
- Create health monitoring and alerting system

## Phase 5: Testing & Validation (Days 11-12)
**Objective:** Comprehensive testing of containerized system

### 5.1 Local Testing
- Test all services in Docker containers locally
- Validate configuration injection and service communication
- Perform end-to-end workflow testing

### 5.2 Multi-Tenant Testing
- Test multiple client configurations simultaneously
- Validate data isolation and security boundaries
- Performance testing under multi-tenant load

### 5.3 Coolify Deployment Testing
- Deploy to Coolify environment with test configuration
- Validate automated provisioning workflow
- Test client onboarding and configuration management

## Phase 6: Production Deployment (Days 13-14)
**Objective:** Deploy production-ready multi-tenant system

### 6.1 Production Environment Setup
- Install and configure Coolify on Linode server
- Set up SSL certificates and domain configuration
- Configure monitoring and logging systems

### 6.2 Client Provisioning System
- Deploy client onboarding FastAPI application
- Create administrative dashboard for client management
- Implement billing and resource tracking (if required)

### 6.3 Documentation & Training
- Create comprehensive deployment documentation
- Document client onboarding procedures
- Create troubleshooting guides and operational procedures

## Technical Implementation Details

### Docker Architecture
```
TM-Base-Image (Ubuntu + Python + Node.js)
├── TM-Tiger (ML Processing)
├── TM-Monkey (Document Generation)  
├── TM-Dashboard (Web Interface)
└── TM-Browser (PDF Generation)
```

### Configuration Strategy
```json
{
  "client_id": "firm_001",
  "firm": {
    "name": "Client Law Firm",
    "masthead": "Custom Legal Services",
    "login_title": "Firm Portal"
  },
  "branding": {
    "logo_url": "/assets/firm_logo.png",
    "primary_color": "#1a365d",
    "theme": "professional"
  },
  "services": {
    "domain": "firm001.tm-platform.com",
    "ssl_enabled": true,
    "auth_required": true
  }
}
```

### Multi-Tenant Deployment Flow
```
Client Form → JSON Generation → Coolify API → Docker Deployment → DNS Configuration → Client Access
```

## Resource Requirements
- **Development Time**: 14 days
- **Linode Resources**: 8GB RAM, 4 CPU cores, 160GB SSD (for 5-10 clients)
- **Coolify Setup**: 1 day for platform installation and configuration
- **Per-Client Resources**: ~500MB RAM, 0.5 CPU cores, 10GB storage

## Risk Mitigation
- **Data Isolation**: Container-level separation with volume mounting
- **Configuration Validation**: JSON schema validation at deployment
- **Rollback Capability**: Version-controlled Docker images with rollback procedures
- **Monitoring**: Health checks and resource monitoring for all client instances

## Success Metrics
- **Deployment Time**: <5 minutes per new client
- **Resource Efficiency**: <500MB RAM per client instance
- **Reliability**: 99.9% uptime for client services
- **Scalability**: Support for 10+ clients on single Linode box

This comprehensive plan transforms the TM system into a scalable, multi-tenant SaaS platform while maintaining the high-quality legal document processing capabilities that make it valuable to law firms.