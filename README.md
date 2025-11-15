# MBBuddy (My Brainstorming Buddy)

###### 點此進入中文版： [`README_TW.md`](README_TW.md)

## 📱 Application Overview

**MBBuddy** is a local private AI interactive platform specifically designed for "internal discussion collaboration", integrating anonymous opinion collection, real-time voting, AI intelligent assistants, and automatic summarization functions to provide a brand-new discussion and interaction experience.

### Core Features:

- **Anonymous Opinion Expression**: Participants can submit opinions anonymously, lowering the psychological barrier to speaking up
- **Real-time Voting Mechanism**: Quick positive/negative voting on submitted opinions, highlighting consensus and divergence
- **Local AI Assistant**: Provides real-time discussion information integration and summaries without cloud connection
- **Cross-device Support**: Hosts can manage discussions on computers while participants can join by scanning QR codes with their phones
- **PDF Report Export**: One-click generation of complete discussion records including chart analysis

### Technical Highlights:

- **Privacy Security**: Complete local inference with no cloud data transmission, ensuring discussion information security
- **NPU Acceleration**: Supports Qualcomm Snapdragon X series device NPU acceleration, enhancing AI processing performance
- **Lightweight Deployment**: Frontend-backend separation architecture, easily deployable in various environments
- **Interactive Experience**: Real-time updated voting mechanisms and discussion timers enhance discussion participation

## 👥 Competition Team Members

| Name | Email |
| --- | --- |
| 趙祖威 | t110ab0012@ntut.org.tw |
| 賴聖元 | 11046015@ntub.edu.tw |
| 吳承諺 | t111ab0011@ntut.org.tw |
| 陳以珊 | t112ab0025@ntut.org.tw |
| 林佑亦 | t112ab0004@ntut.org.tw |

## 📦 Installation and Usage Guide

### 1. Download Project

```bash
git clone https://github.com/UIE47061/MBBuddy.git
cd MBBuddy
```

### 2. Installation Method (One-Click Install)

Run the one-click installation script to automatically complete Docker installation, AnythingLLM setup, and service deployment:

```batch
# Double-click to run or execute in command prompt
scripts\0_one_click_install_TW.bat
```

**Installation steps include**:
- Automatically check and install Docker Desktop
- Guide download and setup of AnythingLLM
- Obtain API keys and configure environment variables
- One-click deployment of MBBuddy production environment
- Display access addresses and control commands upon completion


### 3. Query Your IP Address (Local Network Access)

```bash
# Windows (Command Prompt)
ipconfig | findstr "IPv4"

# Will display something like:
#      IPv4 Address. . . . . . . . . . . . : 192.168.0.114                (Windows)
# Then 192.168.0.114 will be your IP address!
```

**Access addresses**:
- Frontend: `http://[Your IP Address]`
- Backend: `http://[Your IP Address]:8000`

### Stop Development Services

```bash
# Windows - Stop development services
scripts\stop_dev.bat
```

## 📱 Usage Flow

1. **Create Discussion Room**:
   - Enter discussion topic on the homepage
   - Click "Create Discussion Room" button
   - Fill in discussion settings (name, topics, time, etc.)

2. **Invite Participants**:
   - Use generated QR Code or link to invite participants
   - Participants can join by scanning the QR Code

3. **Start Discussion**:
   - Host can initiate, pause, or end discussions
   - Set countdown timer
   - Switch discussion topics at any time

4. **Interactive Participation**:
   - Participants submit opinions/questions
   - Vote on others' opinions (agree/disagree)
   - View real-time sorted opinion lists

5. **AI Assistance**:
   - Click "AI Summary" to get current discussion summary
   - AI can automatically generate agenda topic suggestions

6. **Export Results**:
   - Click "Export PDF" after discussion ends
   - Get complete discussion records including opinions, voting statistics, and chart analysis

## ⚡ Snapdragon X Series Device NPU Acceleration

If using Snapdragon X series laptops, NPU acceleration can be enabled:

1. Confirm installation of latest Windows 11 and NPU drivers
2. Modify model loading parameters in `ai_api.py`:
   ```python
   llm = Llama(
       model_path=MODEL_PATH, 
       n_ctx=2048,
       n_gpu_layers=0,  # Do not use GPU
       n_threads=8,     # CPU thread count
       n_npu_layers=20  # Enable NPU acceleration
   )
   ```

## 📂 Directory Structure
```
MBBuddy/
├── 📁 backend/                      # FastAPI backend service
│   ├── main.py                      # Backend main entry point
│   ├── requirements.txt             # Python dependencies
│   └── api/                         # API modules
│       ├── __init__.py              # Package initialization
│       ├── ai_api.py                # AI-related APIs (model inference, summary)
│       ├── ai_client.py             # AI client
│       ├── ai_config.py             # AI configuration settings
│       ├── ai_prompts.py            # AI prompt templates
│       ├── hostStyle_api.py         # Host style API
│       ├── local_llm_client.py      # Local LLM client
│       ├── mindmap_api.py           # Mind map API
│       ├── network_api.py           # Network-related APIs
│       ├── participants_api.py      # Discussion participation APIs (user management, voting)
│       ├── pdf_generate.py          # PDF generation
│       ├── snapdragon_config.py     # Snapdragon NPU configuration
│       └── transparent_fusion.py    # Transparent fusion functionality
│
├── 🎨 frontend/                     # Frontend application
│   ├── index.html               # Main HTML template
│   ├── package.json             # Frontend dependency configuration
│   ├── vite.config.js           # Vite build configuration
│   ├── public/                  # Static resources
│   │   └── AIresult.txt         # AI result example
│   └── src/                     # Source code directory
│       ├── App.vue              # Root component
│       ├── main.js              # Application entry point
│       ├── assets/              # Style resources
│       │   ├── base.css         # Base styles
│       │   ├── main.css         # Main styles
│       │   └── styles.css       # Custom styles
│       ├── components/          # Vue components
│       │   ├── ControlPanel.vue       # Control panel
│       │   ├── CreateRoomModal.vue    # Create room modal
│       │   ├── Home.vue               # Home component
│       │   ├── HostPanel.vue          # Host panel
│       │   ├── JoinRoomModal.vue      # Join room modal
│       │   ├── MindMapModal.vue       # Mind map modal
│       │   ├── NicknameModals.vue     # Nickname setting modal
│       │   ├── NotificationToast.vue  # Notification message
│       │   ├── ParticipantPanel.vue   # Participant panel
│       │   ├── QRCodeModal.vue        # QR Code modal
│       │   ├── QuestionsList.vue      # Questions list
│       │   ├── ScoreJudgePanel.vue    # Scoring panel
│       │   ├── TimerModal.vue         # Timer modal
│       │   ├── TopicEditModal.vue     # Topic edit modal
│       │   └── TopicsSidebar.vue      # Topic sidebar
│       ├── composables/         # Vue Composition API
│       │   └── useRoom.js       # Discussion room logic
│       ├── router/              # Route configuration
│       │   └── index.js         # Route definitions
│       └── utils/               # Utility functions
│           └── api.js           # API request wrapper
│
├── 🐳 docker/                       # Docker deployment configuration
│   ├── README.md                    # Docker usage instructions
│   ├── docker-compose.yml          # Production environment configuration
│   ├── docker-compose.dev.yml      # Development environment configuration
│   ├── Dockerfile.backend          # Backend container configuration
│   ├── Dockerfile.frontend         # Frontend production container configuration
│   ├── Dockerfile.frontend.dev     # Frontend development container configuration
│   └── nginx.conf                  # Nginx configuration
│
├── 📥 scripts/                      # Automation scripts directory
│   ├── 0_one_click_install_TW.bat   # One-click install script (Chinese)
│   ├── 0_one_click_install_US.bat   # One-click install script (English)
│
└── 📄 Documentation
    ├── README.md                   # Project documentation (this file)
    └── LICENSE                     # MIT license terms
```

### 📋 Key File Descriptions

| File/Directory | Function Description |
|-----------|----------|
| `backend/api/ai_api.py` | Core AI functionality, including text generation and discussion summaries |
| `backend/api/ai_client.py` | AI client, handling AI model loading and inference |
| `backend/api/participants_api.py` | Discussion participation logic, user management and voting system |
| `backend/api/mindmap_api.py` | Mind map functionality, AI automatically generates discussion context |
| `backend/api/transparent_fusion.py` | Transparent fusion technology, integrating multiple AI services |
| `backend/api/snapdragon_config.py` | Snapdragon NPU acceleration configuration |
| `frontend/src/components/` | Vue components, implementing various UI functions |
| `frontend/src/composables/useRoom.js` | Discussion room state management and WebSocket communication |
| `docker/` | Containerized deployment configuration, supporting development and production environments |
| `scripts/` | Automation scripts directory, including installation, deployment, and development environment management |
| `scripts/0_one_click_install_TW.bat` | Windows one-click installation script, automated complete installation process |

## 🛡️ Privacy Protection

This system performs complete local inference with no cloud data transmission. Any discussion messages, AI discussions, and decision-making processes **will not be leaked**. It is particularly suitable for organizations and teams that require high privacy and high security.

## Troubleshooting Common Issues:

1. **First Launch**: Initial download and build may take longer, especially since AI model files are large
2. **Memory Requirements**: Ensure Docker has sufficient memory to load AI models (8GB+ recommended)
3. **Port Conflicts**: Ensure ports 80, 5173, 8000, 8001 are not occupied by other services
4. **IP Changes**: Frontend will automatically detect and connect to the correct backend port, no manual configuration needed

### When Unable to Access from Other Devices
1. Ensure all devices are connected to the same WiFi network
2. Check "Firewall" settings
3. Confirm IP address is correct

## 📄 License Information

This project is licensed under [MIT License](https://choosealicense.com/licenses/mit/), allowing free use, modification, and distribution of this code, but please retain the original license statement.