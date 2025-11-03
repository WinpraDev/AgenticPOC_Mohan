# 🚀 Quick Start Guide

**Get Meta-Agent running in 5 minutes**

---

## Prerequisites

- ✅ MacBook Pro M4, 16GB RAM
- ✅ Python 3.11 installed
- ✅ LM Studio installed
- ✅ Docker Desktop installed
- ✅ WinPrA Agentic POC project available

---

## Step-by-Step Setup

### 1. Start the Database (30 seconds)

```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
docker-compose up -d postgres

# Verify it's running
docker ps | grep dscr_poc_postgres
```

**Expected**: Container `dscr_poc_postgres` is running on port 5433

---

### 2. Setup Project (2 minutes)

```bash
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/AgenticPOC_New"

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with database configuration
./setup_env.sh
```

**Expected**: `.env` file created with DSCR POC database connection

---

### 3. Start LM Studio (1 minute)

1. Open LM Studio application
2. Load model: **qwen2.5-coder-7b-instruct-mlx**
3. Click "Local Server" tab
4. Click "Start Server" (port 1234)

**Expected**: Server shows "Running on http://localhost:1234"

---

### 4. Verify Everything Works (30 seconds)

```bash
python test_setup.py
```

**Expected output:**
```
✓ Configuration loaded
✓ LM Studio connected successfully
✓ PostgreSQL connected successfully
✓ Docker is available
✓ All tools imported successfully

✓ ALL REQUIRED TESTS PASSED
```

---

## 🎉 You're Ready!

### Run Your First Example

```bash
python simple_example.py
```

**This will:**
1. Analyze: "Calculate DSCR for properties from PostgreSQL"
2. Design: 2-agent architecture (DataAgent + CalcAgent)
3. Generate: YAML specifications
4. Generate: Python code (~150 lines)
5. Validate: Syntax & security
6. Write: Files to `generated_agents/` and `agent_specs/`

**Time**: ~2-4 minutes  
**Output**: Working agent files ready to use

---

## Database Configuration

### Connection Details

```
Database: dscr_poc_db
User: dscr_user
Password: dscr_password_change_me
Host: localhost
Port: 5433
```

**Full details**: See `DATABASE_CONFIG.md`

---

## Troubleshooting

### Database Not Connected

```bash
# Check if database container is running
docker ps | grep dscr_poc_postgres

# If not running, start it
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
docker-compose up -d postgres
```

### LM Studio Not Connected

1. Ensure LM Studio app is open
2. Check model is loaded (green indicator)
3. Check "Local Server" is started
4. Verify port 1234 in use: `lsof -i :1234`

### Configuration Error

```bash
# Recreate .env file
./setup_env.sh

# Or manually check .env exists and has correct values
cat .env
```

---

## What's Available

### Current Capabilities

✅ **Requirement Analysis** - Parse natural language  
✅ **Architecture Design** - Design agent systems  
✅ **Spec Generation** - Create YAML specifications  
✅ **Code Generation** - Generate Python code  
✅ **Code Validation** - Syntax & security checks  
✅ **File Operations** - Write agent files  

### Working Example

`simple_example.py` demonstrates the complete pipeline end-to-end.

---

## Next Steps

### Explore What's Built

```bash
# View generated agents
ls -la generated_agents/agents/

# View specifications  
ls -la agent_specs/

# Read the code
cat generated_agents/agents/dataagent.py
```

### Read Documentation

- **README.md** - Complete documentation
- **DATABASE_CONFIG.md** - Database details
- **BUILD_STATUS.md** - What's built, what's next

### Continue Building

The foundation is complete. Next phase: Build remaining tools and orchestrator.

---

## System Status

```
✅ Project structure
✅ Configuration system
✅ LLM client
✅ 4 core tools
✅ Validators
✅ File operations
✅ Database integration (DSCR POC)
✅ Testing infrastructure
✅ Documentation

⏳ 11 remaining tools
⏳ Meta-Agent orchestrator
⏳ Error recovery
⏳ Test generation
```

**Progress**: 60% complete

---

## Quick Commands

```bash
# Verify setup
python test_setup.py

# Run example
python simple_example.py

# Check database
cd "/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC"
docker-compose ps

# Check LM Studio
curl http://localhost:1234/v1/models

# View logs
tail -f logs/*.log
```

---

**Ready in 5 minutes! 🚀**

