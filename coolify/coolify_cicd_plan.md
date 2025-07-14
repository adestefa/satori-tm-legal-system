# Satori CI/CD Pipeline Implementation Plan

## Phase 1: Infrastructure Setup (Week 1)

### 1.1 Linode VPS Provisioning
- **Test Server**: $12 Nanode 2GB (test.satori-ai-tech.com)
- **Stage Server**: $24 Shared 4GB (stage.satori-ai-tech.com)  
- **Prod Server**: $48 Shared 8GB (app.satori-ai-tech.com)

### 1.2 Automated Coolify Installation

**File: `setup/install-coolify.sh`**
```bash
#!/bin/bash
# Usage: ./install-coolify.sh <IP> <user> <password> <environment>

IP=$1
USER=$2
PASS=$3
ENV=$4

echo "Installing Coolify on $ENV server: $IP"

# SSH and install Coolify
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$IP << 'EOF'
    # Update system
    apt update && apt upgrade -y
    
    # Install Coolify
    curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
    
    # Wait for services to start
    sleep 30
    
    # Test installation
    docker ps > /tmp/coolify-test.log
    systemctl status coolify >> /tmp/coolify-test.log
EOF

# Generate report
./generate-install-report.sh $IP $USER $PASS $ENV
```

### 1.3 Installation Verification & Reporting

**File: `setup/generate-install-report.sh`**
```bash
#!/bin/bash
# Generate comprehensive installation report

IP=$1
USER=$2  
PASS=$3
ENV=$4

REPORT_FILE="reports/coolify-install-$ENV-$(date +%Y%m%d-%H%M%S).txt"

echo "=== Coolify Installation Report - $ENV Environment ===" > $REPORT_FILE
echo "Server IP: $IP" >> $REPORT_FILE
echo "Install Date: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Test Coolify API endpoint
if curl -s http://$IP:8000/api/health | grep -q "ok"; then
    echo "✅ Coolify API: HEALTHY" >> $REPORT_FILE
else
    echo "❌ Coolify API: FAILED" >> $REPORT_FILE
fi

# Test Docker
sshpass -p "$PASS" ssh $USER@$IP "docker --version" >> $REPORT_FILE

# System resources
echo "" >> $REPORT_FILE
echo "=== System Resources ===" >> $REPORT_FILE
sshpass -p "$PASS" ssh $USER@$IP "free -h; df -h" >> $REPORT_FILE

echo "Report saved: $REPORT_FILE"
```

## Phase 2: Pipeline Integration (Week 2)

### 2.1 Enhanced dashd.sh Commands

**New Commands:**
```bash
./dashd.sh -setup test     # Install Coolify on test server
./dashd.sh -setup stage    # Install Coolify on stage server  
./dashd.sh -setup prod     # Install Coolify on prod server

./dashd.sh -pancake <client-name> <app-template> <env>
# Example: ./dashd.sh -pancake acme-law legal-doc-processor test
```

### 2.2 Claude Code Agent Integration Points

**Agent Stations in Pipeline:**

1. **Dev Gate Agent** (`agents/dev-gate.sh`)
   - Code quality review
   - Security scan (gosec, staticcheck)
   - Test coverage verification
   - Performance benchmarks

2. **Test Gate Agent** (`agents/test-gate.sh`)
   - Functional testing suite
   - Integration testing
   - API contract testing
   - Generate defect reports

3. **Stage Gate Agent** (`agents/stage-gate.sh`)
   - Performance testing
   - Security penetration testing
   - Load testing
   - Production readiness checklist

4. **Prod Gate Agent** (`agents/prod-gate.sh`)
   - Add monitoring instrumentation
   - Log aggregation setup
   - Health check endpoints
   - Deployment verification

## Phase 3: Testing Framework (Week 3)

### 3.1 Universal Test Suite Template

**File: `testing/universal-test-suite.yaml`**
```yaml
test_categories:
  security:
    - gosec_scan
    - dependency_check
    - secrets_detection
    - sql_injection_test
    
  performance:
    - memory_leak_test
    - concurrent_user_simulation
    - response_time_benchmarks
    - resource_utilization
    
  functionality:
    - unit_test_coverage_80_percent
    - integration_test_suite
    - api_contract_validation
    - error_handling_verification
    
  reliability:
    - chaos_monkey_testing
    - failover_scenarios
    - data_integrity_checks
    - backup_recovery_test
```

### 3.2 Claude Code Test Runner

**File: `agents/run-test-suite.sh`**
```bash
#!/bin/bash
# Universal test runner with Claude Code integration

APP_ID=$1
ENV=$2

echo "Running universal test suite for App $APP_ID in $ENV"

# Run Claude Code agent for test execution
claude-code -p agents/test-executor.md \
  --input "app_id=$APP_ID,environment=$ENV,test_suite=universal-test-suite.yaml" \
  --output "reports/test-report-$APP_ID-$ENV-$(date +%Y%m%d).json"

# Generate human-readable report
claude-code -p agents/test-reporter.md \
  --input "reports/test-report-$APP_ID-$ENV-$(date +%Y%m%d).json" \
  --output "reports/test-summary-$APP_ID-$ENV-$(date +%Y%m%d).txt"
```

## Phase 4: Production Monitoring Setup (Week 4)

### 4.1 Auto-Monitoring Injection

**File: `agents/add-monitoring.sh`**
```bash
#!/bin/bash
# Claude Code agent adds monitoring to Go applications

APP_PATH=$1

# Use Claude Code to inject monitoring
claude-code -p agents/monitoring-injector.md \
  --input "go_app_path=$APP_PATH" \
  --task "Add prometheus metrics, health endpoints, structured logging"

# Verify monitoring endpoints
go test ./monitoring/... -v
```

### 4.2 Production Readiness Checklist

**Auto-generated for each app:**
- ✅ Health check endpoint (`/health`)
- ✅ Metrics endpoint (`/metrics`)
- ✅ Structured JSON logging
- ✅ Graceful shutdown handling
- ✅ Configuration via environment variables
- ✅ Database connection pooling
- ✅ Rate limiting middleware
- ✅ Security headers middleware

## Implementation Timeline

**Week 1**: Infrastructure setup, Coolify installation scripts
**Week 2**: dashd.sh enhancement, basic Claude Code integration
**Week 3**: Universal testing framework, automated test execution
**Week 4**: Production monitoring, end-to-end pipeline testing

## Success Metrics

- **Deployment Time**: < 2 minutes from git push to live
- **Test Coverage**: > 80% automated
- **Security Scans**: 100% of deployments
- **Monitoring**: 100% production apps instrumented
- **Reliability**: 99.9% uptime target

## Directory Structure

```
satori-dev/
├── dash/
│   ├── dashd.sh (enhanced)
│   └── agents/
│       ├── dev-gate.sh
│       ├── test-gate.sh
│       ├── stage-gate.sh
│       └── prod-gate.sh
├── setup/
│   ├── install-coolify.sh
│   └── generate-install-report.sh
├── testing/
│   ├── universal-test-suite.yaml
│   └── test-templates/
├── reports/
│   ├── install-reports/
│   ├── test-reports/
│   └── security-reports/
└── templates/
    ├── legal-doc-processor/
    └── client-configs/
```

This plan gives you a robust, Claude Code-enhanced CI/CD pipeline that maintains your "do less, go faster" philosophy while ensuring enterprise-grade quality and security.