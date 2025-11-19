# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains infrastructure configuration for deploying EdgeLake/AnyLog nodes using Docker Compose. The setup uses a layered configuration approach where each deployment (master, operator, operator2, query) is completely independent with its own configuration.

EdgeLake/AnyLog documentation is located at: `/Users/tviviano/Documents/GitHub/documentation`

## Architecture

The repository uses the **Docker Compose override pattern** for managing multiple independent node deployments:

```
trv-docker-compose/
├── docker-compose.base.yml          # Shared base configuration (volumes, image, network)
├── Makefile                         # Primary interface for all operations
├── .env.root.template              # Environment-wide defaults (copy to .env.root)
└── deployments/
    ├── master/                     # Master node (blockchain coordinator)
    ├── operator/                   # Data operator node
    ├── operator2/                  # Second operator node
    └── query/                      # Query node
        ├── docker-compose.base.yml          # Symlink to ../../docker-compose.base.yml
        ├── docker-compose.override.yml      # Deployment-specific compose config
        ├── .env                             # Deployment overrides
        └── configs/
            ├── base_configs.env             # Core node settings (NODE_TYPE, ports, DB, blockchain)
            └── advance_configs.env          # Advanced settings (OVERLAY_IP, networking, features)
```

### Configuration Priority (highest to lowest)
1. Command-line variables
2. Shell environment variables
3. `.env` file (deployment-specific)
4. `configs/advance_configs.env`
5. `configs/base_configs.env`

### Node Types
- **master**: Blockchain coordinator (ports 32048/32049)
- **operator**: Data storage/processing nodes (ports 32148/32149, different for operator2)
- **query**: Query execution node (ports 32348/32349)

## Commands

### Primary Makefile Commands

All operations use the Makefile from `trv-docker-compose/`:

```bash
# Start/stop individual deployments
make up <type>                # Start deployment (master, operator, operator2, query)
make down <type>              # Stop deployment
make restart <type>           # Restart deployment
make clean <type>             # Stop and remove volumes (deletes data!)

# Monitoring and interaction
make logs <type>              # View logs (follow mode)
make attach <type>            # Attach to EdgeLake CLI (Ctrl-D to detach)
make connect <type>           # Open bash shell in container
make status <type>            # Show deployment status
make info <type>              # Show deployment configuration

# Batch operations
make up-all                   # Start all deployments (master → operators → query)
make down-all                 # Stop all deployments (reverse order)
make restart-all              # Restart all deployments
make clean-all                # Clean all deployments (prompts for confirmation)
make status-all               # Show status of all deployments

# Remote deployment
make sync <type>              # Sync deployment to remote host (uses OVERLAY_IP)
make sync-all                 # Sync all deployments to their remote hosts
make ssh <type>               # SSH to deployment host

# Image management
make pull <type>              # Pull image from registry and tag locally
make rebuild <type>           # Pull image and restart deployment
```

### Alternative Commands (from user's CLAUDE.md)
The user also uses these custom wrapper commands:
```bash
mel down <type>               # Bring down docker service
mel clean <type>              # Clean volumes
mel up <type>                 # Bring service back up
mel down-all                  # Bring down all services
mel clean-all                 # Clean all volumes
mel up-all                    # Bring up all services
```

### Direct Docker Compose (less common)

When working directly with docker-compose (not recommended, use Makefile):

```bash
cd trv-docker-compose/deployments/<type>
docker-compose -f ../../docker-compose.base.yml -f docker-compose.override.yml <command>
```

## Typical Workflows

### Local Development
```bash
cd trv-docker-compose
make up operator              # Start operator node
make logs operator            # Watch logs
make attach operator          # Access EdgeLake CLI
make down operator            # Stop when done
```

### Remote Deployment
```bash
cd trv-docker-compose
make sync operator            # Sync to remote host (uses OVERLAY_IP from configs)
make ssh operator             # SSH to remote host
# On remote:
cd /home/USER/EdgeLake/docker-compose/trv-docker-compose
make up operator
```

### Full Network Deployment
```bash
cd trv-docker-compose
make up-all                   # Starts: master → operators (with delays) → query
make status-all               # Verify all running
```

### Configuration Changes
1. Edit `deployments/<type>/configs/base_configs.env` or `advance_configs.env`
2. For deployment-specific overrides, edit `deployments/<type>/.env`
3. Restart: `make restart <type>`

## Key Configuration Variables

### Core Settings (base_configs.env)
- `NODE_TYPE`: master, operator, or query
- `NODE_NAME`: Container name (e.g., edgelake-master)
- `COMPANY_NAME`: Owner organization
- `ANYLOG_SERVER_PORT`: TCP port for node communication
- `ANYLOG_REST_PORT`: REST API port
- `DB_TYPE`: sqlite or psql
- `BLOCKCHAIN_SOURCE`: master or optimism
- `LEDGER_CONN`: Master node connection (IP:port)

### Advanced Settings (advance_configs.env)
- `OVERLAY_IP`: Network overlay IP (used for remote SSH/sync)
- `REMOTE_CLI`: Enable remote CLI access
- `MCP_AUTOSTART`: Auto-start Model Context Protocol server
- `DISABLE_CLI`: Disable AnyLog CLI interface
- `LOCATION`, `COUNTRY`, `STATE`, `CITY`: Geolocation metadata

### Deployment Overrides (.env)
- `IMAGE`: Docker image name
- `TAG`: Image tag (latest, dev, amd64-latest, etc.)
- `INIT_TYPE`: prod (run EdgeLake) or bash (shell interface)
- `CONN_IP`, `CLI_PORT`: Remote CLI parameters

### Root Configuration (.env.root)
- `DEFAULT_IMAGE`, `DEFAULT_TAG`: Default image/tag for all deployments
- `SSH_USER`: Default SSH user for remote access
- `REGISTRY`: Private Docker registry address
- `REMOTE_DEPLOY_PATH`: Path on remote hosts for syncing
- `DOCKER_SUDO`: Whether to use sudo for docker commands

## Important Notes

### Volume Management
- Each deployment creates volumes prefixed with `${NODE_NAME}`
- Volumes persist data across container restarts
- `make clean <type>` removes volumes and **deletes all data**
- Ensure unique `NODE_NAME` for each deployment to avoid conflicts

### Network Architecture
- All containers use `network_mode: host` for direct host networking
- Port conflicts require different ports in each deployment's `base_configs.env`
- OVERLAY_IP in `advance_configs.env` is used for remote host identification

### Adding New Deployments
1. Copy existing deployment: `cp -r deployments/operator deployments/operator3`
2. Edit `.env`, `configs/base_configs.env`, `configs/advance_configs.env`
3. Ensure unique `NODE_NAME` and ports
4. Start: `make up operator3`

### Migration from Old Structure
This replaces the `docker-makefiles/` structure that used `EDGELAKE_TYPE` variable and template substitution. The new approach is Docker-native with independent deployments.

## Open Horizon Integration

This repository also includes Open Horizon deployment configurations for managing EdgeLake services via the OH Management Hub.

### OH Management Hub Details
- **Hub Location**: trv-srv-001 (100.127.19.27)
- **Exchange**: http://100.127.19.27:3090/v1
- **CSS**: http://100.127.19.27:9443
- **Key Learnings**: See `OH_HUB_LEARNINGS.md` for detailed documentation

### OH Service Management

```bash
# From local machine, sync and publish services
cd /Users/tviviano/Documents/GitHub/trv-edgelake-infra
make -f Makefile.oh sync          # Sync to hub
make -f Makefile.oh oh-publish-all  # Publish services (run from hub)

# On hub (100.127.19.27)
cd /home/tviviano/trv-edgelake-infra
export HZN_ORG_ID=trv-services
export HZN_EXCHANGE_USER_AUTH=trv-services/admin:YOUR_PASSWORD
make -f Makefile.oh oh-publish-all
```

### Adding New Organizations to OH Hub

When adding a new organization (see `OH_HUB_LEARNINGS.md` for complete details):

1. **Create org and admin user in Exchange**
2. **Configure agbot to serve the new org** (patterns AND business policies)
3. **Verify agbot configuration**
4. **Publish services to new org**

**Critical**: The agbot must have both pattern AND business policy associations for the new org to work properly.

### Edge Device Registration

```bash
# On edge device
sudo tee /etc/default/horizon <<EOF
HZN_EXCHANGE_URL=http://100.127.19.27:3090/v1
HZN_FSS_CSSURL=http://100.127.19.27:9443
EOF

sudo systemctl restart horizon

export HZN_ORG_ID=myorg
export HZN_EXCHANGE_USER_AUTH=myorg/admin:eBzlwoERNzYMl8n9Oa3WHEjf0ja9gK
hzn register --name=node-name --policy=node.policy.json
```

### Current OH Deployments

**Active EdgeLake Network:**
- **Master**: 100.127.19.27:32048 (edgelake-master) - docker-compose
- **Query**: 100.127.19.27:32348 (edgelake-query) - docker-compose
- **Operator 1**: 100.102.221.116:32148 (edgelake-operator) - docker-compose on trv-srv-012
- **Operator 2**: 100.91.209.39:32248 (edgelake-operator-oh) - **Open Horizon on trv-srv-014**

**OH Service Details:**
- **Organization**: myorg
- **Service**: service-edgelake-operator
- **Current Version**: 1.4.3
- **Configuration**: `oh-services/operator/configurations/operator_production.env`
- **Key Settings**:
  - Ports: 32248 (TCP), 32249 (REST), 32150 (Broker)
  - OVERLAY_IP: 100.91.209.39 (Tailscale)
  - CONN_IP: 0.0.0.0 (bind all interfaces)

**Important Notes:**
- OH containers do NOT support TTY - use helper script `~/edgelake-cli.sh` for CLI access
- Only publish ONE version at a time - old deployment policies cause multiple agreements
- When cleaning blockchain, must clean ALL nodes' volumes to remove stale policies
- Unique ports required when multiple operators share same external IP

## Next Phase: Kubernetes + Open Horizon Deployment

**Target**: Deploy EdgeLake operator via OH into Kubernetes cluster

**Environment:**
- **Kubernetes Host**: 100.74.102.38
- **Deployment Method**: Helm chart orchestrated by Open Horizon
- **Network**: Tailscale on host (outside cluster), need ingress to K8s services

**Helm Chart Location:**
```bash
/Users/tviviano/Documents/GitHub/trv-edgelake-infra/helm/
```

**Key Challenges to Address:**
1. OH integration with Kubernetes workload management
2. Ingress configuration for Tailscale → K8s routing
3. OVERLAY_IP configuration when EdgeLake runs inside pod
4. Persistent volume management through OH
5. Port mapping: K8s Service → Pod → EdgeLake container

**Reference Documentation:**
- `OH_HUB_LEARNINGS.md` - Complete OH management guide
- `QUICKSTART_OH.md` - Quick reference for OH operations
- `/Users/tviviano/Documents/GitHub/documentation` - EdgeLake docs

## Decision Points and Workarounds

When implementing workarounds to problems, always get user's approval before progressing.
