# Automatic Archiving Guide

**Version:** 1.3.0  
**Date:** October 28, 2025  
**Status:** ✅ Active

---

## 🎯 Overview

After workflow completion, **all generated files are automatically archived** into a dated folder with proper naming conventions, and the workspace is cleaned up.

---

## 🔄 Updated Workflow (10 Steps)

```
STEP 1: Analyze Requirements ✓
STEP 2: Design Architecture ✓
STEP 3: Generate Specifications ✓
STEP 4: Generate Code ✓
STEP 5: Validate Specifications ✓
STEP 6: Validate Code ✓
STEP 7: Write Files ✓
STEP 8: Deploy System (Single Container) ✓
STEP 9: Setup Monitoring ✓
STEP 10: Archive & Cleanup ✓ ← NEW!
        ↓
Clean Workspace + Organized Archive! 📦
```

---

## 📂 Archive Structure

### Archive Naming Convention

```
archives/
└── {project-name}_{timestamp}/
    └── ...
```

**Example:**
```
archives/
└── calculate-debt-coverage-ratio_20251028_154322/
```

### Inside Each Archive

```
{project-name}_{timestamp}/
├── agent_code/                # Generated agent implementations
│   ├── dataagent.py
│   ├── calcagent.py
│   └── reportagent.py
│
├── specifications/            # YAML specifications
│   ├── dataagent.yaml
│   ├── calcagent.yaml
│   └── reportagent.yaml
│
├── deployment/               # Complete deployment setup
│   └── {system-name}/
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── orchestrator.py
│       ├── run_simulation.py
│       ├── deploy.sh
│       ├── requirements.txt
│       ├── .env.example
│       └── agents/
│           └── ...
│
├── monitoring/               # Monitoring configuration
│   ├── DataAgent/
│   │   ├── health_check.py
│   │   ├── metrics.py
│   │   ├── logging_config.json
│   │   └── alerts.yml
│   ├── CalcAgent/
│   │   └── ...
│   └── ReportAgent/
│       └── ...
│
├── documentation/            # Additional docs (if any)
│
├── ARCHIVE_SUMMARY.md       # Complete summary
└── manifest.json            # Archive metadata
```

---

## 📊 What Happens During Archiving

### Step 10: Archive & Cleanup

1. **Create Archive Directory**
   ```
   archives/calculate-debt-coverage-ratio_20251028_154322/
   ```

2. **Copy All Files**
   - ✅ Agent code files
   - ✅ YAML specifications
   - ✅ Complete deployment directory
   - ✅ Monitoring configurations

3. **Generate Documentation**
   - ✅ ARCHIVE_SUMMARY.md
   - ✅ manifest.json

4. **Clean Up Workspace**
   - ❌ Delete `agent_specs/`
   - ❌ Delete `generated_agents/`
   - ❌ Delete `deployment/`
   - ❌ Delete `monitoring/`

5. **Result: Clean Workspace!**
   ```
   ✓ All files archived
   ✓ Workspace cleaned
   ✓ Ready for next generation
   ```

---

## 📁 Archive Files Explained

### `ARCHIVE_SUMMARY.md`

Complete summary of the archived project:

```markdown
# Archive Summary: Calculate Debt Coverage Ratio

**Archive Name:** calculate-debt-coverage-ratio_20251028_154322
**Created:** October 28, 2025 at 3:43 PM
**Status:** ✅ Complete

## Archive Contents
- Total Files: 24
- Agents: 3
- Deployment: Ready
- Monitoring: Configured
```

### `manifest.json`

Machine-readable metadata:

```json
{
  "project_name": "Calculate Debt Coverage Ratio",
  "archive_name": "calculate-debt-coverage-ratio_20251028_154322",
  "timestamp": "20251028_154322",
  "archived_files": [
    "agent_code/dataagent.py",
    "specifications/dataagent.yaml",
    ...
  ],
  "file_count": 24,
  "created_at": "2025-10-28T15:43:22.123456"
}
```

---

## 🚀 Using Archived Projects

### Navigate to Archive

```bash
cd archives/calculate-debt-coverage-ratio_20251028_154322
```

### Review Contents

```bash
# List all files
find . -type f

# Read summary
cat ARCHIVE_SUMMARY.md

# Check manifest
cat manifest.json | jq .
```

### Deploy from Archive

```bash
# Navigate to deployment
cd deployment/*/

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Deploy
bash deploy.sh
```

### Run Agents

```bash
# Run orchestrator
docker exec <container-name> python orchestrator.py

# Run simulations
docker exec <container-name> python run_simulation.py scenario
```

---

## 🔧 Configuration

### Enable/Disable Cleanup

In `simple_example.py`:

```python
# With cleanup (default)
archive_path = archive_workflow_results(
    project_name=archive_name,
    written_files=written_files,
    deployment_result=deployment_result,
    monitoring_results=monitoring_results,
    cleanup=True  # ← Archives and deletes originals
)

# Without cleanup (keep original files)
archive_path = archive_workflow_results(
    ...
    cleanup=False  # ← Archives but keeps originals
)
```

### Custom Archive Location

```python
from meta_agent.utils.archive_manager import ArchiveManager

# Custom base directory
archive_manager = ArchiveManager(base_archive_dir=Path("/custom/path/archives"))
```

---

## 📊 Benefits

### ✅ Organization
- All project files in one place
- Dated archives for version tracking
- No cluttered workspace

### ✅ Portability
- Self-contained archives
- Easy to share or backup
- Ready to deploy anywhere

### ✅ Clean Workspace
- No leftover files
- Ready for next generation
- Clear separation between projects

### ✅ Documentation
- Auto-generated summaries
- Complete file manifest
- Usage instructions included

### ✅ Version Control
- Timestamped archives
- Easy to compare versions
- Historical record maintained

---

## 📋 Archive Comparison

| Aspect | Before Archiving | After Archiving |
|--------|------------------|-----------------|
| **Workspace** | Cluttered with files | Clean |
| **Organization** | Scattered files | Organized in one folder |
| **Documentation** | Manual | Auto-generated |
| **Deployment** | Find files manually | Ready-to-use |
| **Sharing** | Multiple directories | Single archive |
| **Backup** | Complex | Simple (one folder) |

---

## 🔍 Finding Archives

### List All Archives

```bash
ls -lht archives/
```

### Find by Date

```bash
# Today's archives
find archives/ -name "*$(date +%Y%m%d)*" -type d

# This month
find archives/ -name "*202510*" -type d
```

### Find by Project Name

```bash
find archives/ -name "*debt-coverage*" -type d
```

### Search Archive Contents

```bash
# Find all Python files
find archives/ -name "*.py" -type f

# Find specific agent
find archives/ -name "*calcagent*"
```

---

## 💾 Backup Strategies

### Backup Single Archive

```bash
# Create tarball
tar -czf backup.tar.gz archives/calculate-debt-coverage-ratio_20251028_154322/

# Zip archive
zip -r backup.zip archives/calculate-debt-coverage-ratio_20251028_154322/
```

### Backup All Archives

```bash
# Backup all to external drive
rsync -av archives/ /Volumes/Backup/meta-agent-archives/

# Create dated backup
tar -czf archives_backup_$(date +%Y%m%d).tar.gz archives/
```

### Cloud Backup

```bash
# AWS S3
aws s3 sync archives/ s3://my-bucket/meta-agent-archives/

# Google Drive (with rclone)
rclone sync archives/ gdrive:meta-agent-archives/
```

---

## 🧹 Archive Management

### Clean Old Archives

```bash
# Remove archives older than 30 days
find archives/ -type d -mtime +30 -exec rm -rf {} +

# Keep only last 10 archives
ls -t archives/ | tail -n +11 | xargs rm -rf
```

### Archive Size Management

```bash
# Check archive sizes
du -sh archives/*/

# Find large archives
find archives/ -type d -exec du -sh {} + | sort -rh | head -10

# Compress old archives
find archives/ -type d -mtime +7 -exec tar -czf {}.tar.gz {} \; -exec rm -rf {} \;
```

---

## 📊 Monitoring Archives

### Archive Statistics

```bash
# Count archives
ls -1 archives/ | wc -l

# Total archive size
du -sh archives/

# Average archive size
du -s archives/*/ | awk '{sum+=$1} END {print sum/NR/1024/1024 " MB"}'
```

### Archive Growth

```bash
# Track archive creation
find archives/ -type d -newermt "7 days ago" | wc -l

# Archives per day
find archives/ -type d | grep -o '[0-9]\{8\}' | sort | uniq -c
```

---

## 🆘 Troubleshooting

### Archive Not Created?

**Check permissions:**
```bash
ls -la archives/
```

**Check disk space:**
```bash
df -h .
```

### Files Not Cleaned Up?

**Verify cleanup setting:**
```python
# Check in simple_example.py
cleanup=True  # Should be True for cleanup
```

### Cannot Find Archive?

**List all archives:**
```bash
find archives/ -type d -maxdepth 1
```

**Check archive path:**
```bash
# Path shown in workflow output
cat logs/orchestrator.log | grep "Archive created"
```

---

## 💡 Best Practices

### 1. Regular Cleanup
```bash
# Weekly cleanup of old archives
find archives/ -type d -mtime +30 -exec rm -rf {} +
```

### 2. Descriptive Project Names
```python
# ✅ Good
"calculate-dscr-for-orlando-mall"

# ❌ Bad
"test1"
```

### 3. Backup Important Archives
```bash
# Before cleanup
cp -r archives/important-project_* ~/backups/
```

### 4. Document Custom Changes
```bash
# Add notes to archive
echo "Custom modifications: ..." >> archives/*/NOTES.txt
```

### 5. Test Before Deployment
```bash
# Always test from archive
cd archives/latest/deployment/*/
bash deploy.sh
```

---

## 📚 Summary

| Feature | Description |
|---------|-------------|
| **Automatic** | Archives created after each workflow |
| **Organized** | Structured folders with clear naming |
| **Documented** | Auto-generated summaries and manifests |
| **Clean** | Workspace cleaned after archiving |
| **Portable** | Self-contained, ready-to-deploy archives |
| **Timestamped** | Easy version tracking |

---

**Your workspace stays clean, projects stay organized!** 📦✨

