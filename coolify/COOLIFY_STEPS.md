# COOLIFY_STEPS.md: Automated Coolify Installation Guide

**Version:** 1.0
**Purpose:** This guide provides the official step-by-step procedure for installing and verifying Coolify on a new server. It uses the `coolify_install_scripts.sh` automation script, which is the production-ready tool for this task.

---

## 1. Overview

This process automates the installation of Coolify, our chosen platform for CI/CD and application hosting. The `coolify_install_scripts.sh` script handles all dependencies, performs the installation, and generates a comprehensive report to verify success.

This setup is the foundational step for enabling the Git-driven deployment workflow orchestrated by `dashd.sh`.

---

## 2. Prerequisites

Before you begin, ensure you have the following information for the target server (e.g., a fresh Linode VPS):

- **IP Address:** The public IP address of the server.
- **User:** A user with `sudo` privileges (e.g., `root`).
- **Password:** The password for the specified user.
- **Environment Name:** The role of the server (e.g., `test`, `stage`, `prod`).
- **(Optional) Domain:** The domain or subdomain you plan to point to this server.

---

## 3. Installation Procedure

Follow these steps from your local machine to provision a remote server.

### Step 1: Navigate to the Dash Directory

All operations should be run from the `dash` project directory.

```bash
cd /Users/corelogic/satori-dev/dash
```

### Step 2: Make the Script Executable

Ensure the installation script has the necessary permissions to run.

```bash
chmod +x coolify_install_scripts.sh
```

### Step 3: Run the Automated Installer

Execute the script with the server credentials and environment details. The script will handle everything from installing dependencies (`sshpass`, `docker`) to running the Coolify installer and verifying the result.

**Example for the `test` environment:**

```bash
./coolify_install_scripts.sh 96.126.111.186 root 'YOUR_SERVER_PASSWORD' test test.satori-ai-tech.com
```

**Example for a `stage` environment:**

```bash
./coolify_install_scripts.sh 192.0.2.2 root 'YOUR_SERVER_PASSWORD' stage stage.satori-ai-tech.com
```

The installation will take 3-5 minutes. The script will provide real-time feedback on its progress.

---

## 4. Post-Installation Verification

Once the script finishes, it provides two key assets for verification.

### Step 4a: Review the Installation Report

A detailed report will be saved in the `reports/` directory (e.g., `reports/coolify-install-test-20250626-103000.txt`).

This report contains:
- Installation duration and status.
- Accessibility of the Coolify Web UI and API.
- Remote server resource information (CPU, RAM, Disk).
- A "Next Steps" section guiding you on DNS configuration and initial setup.

**To view the report:**
```bash
cat reports/coolify-install-test-*.txt
```

### Step 4b: Use the `check-server.sh` Helper Script

The installer also generates a convenient `check-server.sh` script in the current directory. You can use this anytime to get a quick status update on your new Coolify instance.

**To check the server status:**
```bash
./check-server.sh 96.126.111.186 root 'YOUR_SERVER_PASSWORD'
```
**Expected Output:**
```
🔍 Checking server status...
Web Interface: ✅ UP
SSH Access: Connected
Docker: (List of running Coolify containers)
```

---

## 5. Final Manual Steps

The automation handles the technical installation. The final steps require manual intervention:

1.  **DNS Configuration:** Point your domain's A record (e.g., `test.satori-ai-tech.com`) to the server's IP address.
2.  **Coolify Setup Wizard:** Access the Coolify dashboard in your browser at `http://<YOUR_IP_OR_DOMAIN>:8000`.
3.  **Complete the Wizard:** Follow the on-screen instructions to create your admin account and configure Coolify.

Once these steps are complete, the server is fully provisioned and ready to be integrated into the `dashd.sh` GitOps workflow.
