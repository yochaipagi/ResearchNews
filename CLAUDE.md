# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Starting the Application
- `./run.sh` - Interactive setup and start script (preferred method)
- `docker-compose up -d` - Start all services in detached mode
- `docker-compose down` - Stop all services

### Backend Development
- `cd backend && uvicorn main:app --reload` - Run backend in development mode
- `python test_gemini.py` - Test Gemini API integration
- `python gemini_examples.py` - Run summarization examples
- `python gemini_examples.py --list-models` - List available Gemini models

### Frontend Development
- `cd frontend && npm run dev` - Start Next.js development server
- `cd frontend && npm run build` - Build for production
- `cd frontend && npm run lint` - Run ESLint

### Database Management
- `python backend/setup_db.py` - Initialize database schema
- Database runs on PostgreSQL with pgvector extension

## Architecture Overview

### System Components
- **Backend**: FastAPI application with Celery for background tasks
- **Frontend**: Next.js 14 with Next-Auth for authentication
- **Database**: PostgreSQL with pgvector for vector embeddings
- **Task Queue**: Redis + Celery for async paper processing
- **LLM Integration**: Google Gemini (primary) or OpenAI (fallback)

### Key Data Models
- `Paper`: Stores arXiv papers with AI-generated summaries (`backend/app/models.py:19`)
- `UserAccount`: User profiles with category preferences (`backend/app/models.py:42`)
- `UserSaved`: Many-to-many relationship for saved papers (`backend/app/models.py:63`)

### Background Tasks (`backend/app/tasks.py`)
- Paper ingestion runs every 3 hours via Celery Beat
- Summary generation processes unsummarized papers hourly
- Digest emails sent based on user frequency preferences (daily/weekly/monthly)

### API Structure (`backend/app/api.py`)
- Authentication uses simplified Bearer token system
- Admin endpoints require email to be in `ADMIN_EMAILS` setting
- Paper feed supports pagination and category filtering

### Frontend Architecture
- Landing page at `frontend/pages/index.tsx`
- Authentication flow through Next-Auth with Google OAuth
- User onboarding for category selection and digest preferences

## Environment Configuration
- `.env` file required with `GOOGLE_API_KEY` (use `./setup-env.sh` to create)
- `LLM_PROVIDER` can be set to "gemini" (default) or "openai"
- Docker Compose handles service orchestration with health checks

## Development URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs (Swagger UI)
- Alternative API docs: http://localhost:8000/redoc

## Testing and Examples
- `test_gemini.py` verifies API integration and provides error diagnostics
- `gemini_examples.py` demonstrates various summarization techniques
- Use `python gemini_examples.py --model MODEL_NAME` to test specific models

---

# 📱 iOS App Transformation Project

## 🎯 Project Vision
Transforming from an email digest service to a native iOS app with infinite scrolling arXiv papers and on-demand AI summarization.

## 🏗 Architecture Transformation

### Current State (Email Digest)
- **Frontend**: Next.js web application
- **Backend**: FastAPI with scheduled digest emails
- **User Flow**: Email subscriptions → Scheduled digests → Email delivery

### Target State (iOS App)
- **Frontend**: Native iOS app with SwiftUI
- **Backend**: Enhanced FastAPI with mobile-optimized endpoints
- **User Flow**: Infinite scroll → Tap paper → AI summary on-demand

## 📋 Development Phases

### Phase 1: Backend API Enhancement (Days 1-3)
**Goal**: Optimize existing FastAPI for mobile consumption

**New Endpoints**:
- `GET /api/v2/papers/feed` - Cursor-based pagination for infinite scroll
- `POST /api/v2/papers/{id}/summarize` - On-demand AI summary generation
- `GET /api/v2/papers/search` - Full-text search with category filters
- `GET /api/v2/categories/trending` - Popular categories and topics

**Enhancements**:
- Add Redis caching for frequently accessed summaries
- Implement cursor-based pagination for better performance
- Add summary generation timestamps and caching logic
- Create mobile-optimized response formats

### Phase 2: iOS App Foundation (Days 4-7)
**Goal**: Create SwiftUI app with infinite scrolling feed

**Key Components**:
- `FeedView` - Main infinite scrolling paper list
- `PaperCardView` - Individual paper display with summary button
- `NetworkManager` - API communication with URLSession
- `PaperStore` - ObservableObject for state management

**Core Features**:
- Infinite scroll with pagination
- Pull-to-refresh functionality
- Basic paper display (title, authors, abstract preview)
- Loading states and error handling

### Phase 3: AI Integration (Days 8-10)
**Goal**: Implement tap-to-summarize functionality

**Features**:
- Tap paper card to trigger AI summarization
- Loading animations during summary generation
- Summary display in modal or expanded card view
- Cache summaries locally for offline access
- Retry mechanism for failed summarizations

### Phase 4: Advanced Features (Days 11-14)
**Goal**: Polish and enhance user experience

**Features**:
- Advanced filtering (categories, date ranges, keywords)
- Search functionality with real-time results
- Bookmark/save papers for later reading
- Dark/light mode support
- Share functionality for papers and summaries

## 🛠 Technical Implementation Details

### iOS App Structure
```
iOS/
├── ResearchFeed/
│   ├── Views/
│   │   ├── FeedView.swift
│   │   ├── PaperCardView.swift
│   │   ├── FilterView.swift
│   │   └── SummaryModalView.swift
│   ├── Models/
│   │   ├── Paper.swift
│   │   ├── Category.swift
│   │   └── APIResponse.swift
│   ├── Services/
│   │   ├── NetworkManager.swift
│   │   ├── CacheManager.swift
│   │   └── BookmarkManager.swift
│   └── Stores/
│       └── PaperStore.swift
```

### Backend API Enhancements
**New Models**:
- Add `summary_generated_at` to Paper model
- Add `view_count` and `summary_count` for trending metrics
- Create `SearchQuery` model for search functionality

**Caching Strategy**:
- Redis cache for popular papers and summaries
- 1-hour TTL for summaries, 24-hour for paper metadata
- Cache invalidation on paper updates

### Data Flow
1. **App Launch**: Fetch initial batch of papers (20-50 items)
2. **Infinite Scroll**: Load more papers as user scrolls
3. **Tap Paper**: Generate summary on-demand, cache result
4. **Filter/Search**: Real-time filtering with debounced API calls

## 🔧 Development Commands

### iOS Development
- `cd iOS && open ResearchFeed.xcodeproj` - Open Xcode project
- `xcodebuild -scheme ResearchFeed build` - Build iOS app from command line
- `xcrun simctl list devices` - List available iOS simulators

### API Development
- `cd backend && python -m pytest tests/` - Run API tests
- `cd backend && python -c "from app.api import app; print(app.routes)"` - List all routes
- `curl -X GET "http://localhost:8000/api/v2/papers/feed?limit=10"` - Test mobile API

### Testing Mobile API
- `python test_mobile_api.py` - Test mobile-specific endpoints
- `curl -X POST "http://localhost:8000/api/v2/papers/1/summarize"` - Test on-demand summarization

## 🔀 Git Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/ios-backend-api` - Phase 1 backend enhancements
- `feature/ios-app-foundation` - Phase 2 iOS app structure
- `feature/ai-integration` - Phase 3 summarization features
- `feature/advanced-features` - Phase 4 polish and extras

### Commit Conventions
- `feat: add mobile API endpoint for paper feed`
- `fix: resolve pagination cursor encoding issue`
- `docs: update API documentation for mobile endpoints`
- `refactor: optimize summary caching logic`

### Major Milestones
- `v1.0-backend` - Mobile API ready
- `v1.0-ios-mvp` - Basic iOS app with infinite scroll
- `v1.0-ai-ready` - AI summarization integrated
- `v1.0-release` - Full-featured iOS app

## 🎯 What We Keep vs Transform

### ✅ Keep & Enhance
- Paper ingestion system (`backend/app/ingestion.py`)
- AI summarization logic (`backend/app/summarise.py`)
- Database models (with minor additions)
- Celery background tasks for paper fetching
- Settings and configuration system
- Docker infrastructure for backend

### 🔄 Transform
- API endpoints → Mobile-optimized versions
- Authentication → iOS Keychain integration
- Frontend → Native iOS SwiftUI app
- User management → Simplified for mobile

### ❌ Remove
- Email digest functionality
- Next.js frontend and components
- Web-specific authentication (Next-Auth)
- Scheduled digest tasks
- Frontend Docker containers

## 📱 iOS App Features

### Core Features
- **Infinite Scroll**: Smooth pagination with cursor-based loading
- **On-Demand AI**: Tap any paper to generate summary instantly
- **Smart Caching**: Offline access to viewed papers and summaries
- **Advanced Filtering**: Multi-select categories, date ranges, keywords
- **Search**: Real-time search across titles, authors, and abstracts

### User Experience
- **Performance**: Sub-200ms response times for cached content
- **Offline**: Read cached papers and summaries without internet
- **Accessibility**: VoiceOver support, dynamic text sizing
- **Responsive**: Optimized for all iPhone sizes

## 🚀 Success Metrics
- **Performance**: <2s load time for 50 papers
- **AI Quality**: >85% user satisfaction with summaries
- **Usage**: >50% of users tap for summaries
- **Retention**: >70% weekly active users return

This transformation maintains the core value proposition (AI-powered arXiv paper discovery) while dramatically improving the user experience through native mobile interfaces and real-time interaction.