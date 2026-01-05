# Frontend Development Plan - Arrakis-Marketeer
## React + TypeScript Email Marketing Platform

---

## 1. TECH STACK

### Core Framework
- **React 18+** with TypeScript
- **Vite** for build tooling (fast dev server, optimized builds)
- **React Router v6** for routing

### State Management
- **React Query (TanStack Query)** for server state & API caching
- **Zustand** for client state (auth, UI preferences)
- **React Hook Form** for form state management

### UI Framework & Styling
- **Tailwind CSS** for utility-first styling
- **shadcn/ui** for pre-built accessible components
- **Radix UI** for headless component primitives
- **Lucide React** for icons
- **Framer Motion** for animations

### API & Authentication
- **Axios** for HTTP client with interceptors
- **JWT** token management (access + refresh)
- **React Query** for async state

### Rich Text Editor
- **Tiptap** or **Lexical** for email content editing
- **React Email** for email template rendering

### Additional Tools
- **Zod** for runtime validation
- **date-fns** for date manipulation
- **React Hot Toast** for notifications
- **React Helmet Async** for SEO

---

## 2. PROJECT STRUCTURE

```
frontend/
├── public/
│   ├── favicon.ico
│   └── og-image.png
├── src/
│   ├── api/                    # API client & services
│   │   ├── client.ts           # Axios instance with interceptors
│   │   ├── auth.api.ts         # Auth endpoints
│   │   ├── campaigns.api.ts    # Campaign endpoints
│   │   └── ai.api.ts           # AI generation endpoints
│   ├── assets/                 # Static assets
│   │   ├── images/
│   │   └── logos/
│   ├── components/             # Reusable components
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── layout/             # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── auth/               # Auth-related components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── SignupForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── campaigns/          # Campaign components
│   │   │   ├── CampaignCard.tsx
│   │   │   ├── CampaignList.tsx
│   │   │   ├── CampaignForm.tsx
│   │   │   ├── CampaignStats.tsx
│   │   │   └── ObjectiveManager.tsx
│   │   ├── ai/                 # AI generation components
│   │   │   ├── GenerationForm.tsx
│   │   │   ├── VariantCard.tsx
│   │   │   ├── JobStatusPoll.tsx
│   │   │   └── SubjectLineGenerator.tsx
│   │   └── common/             # Common components
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── Pagination.tsx
│   │       └── ConfirmDialog.tsx
│   ├── hooks/                  # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useCampaigns.ts
│   │   ├── useAIGeneration.ts
│   │   └── useDebounce.ts
│   ├── layouts/                # Page layouts
│   │   ├── AuthLayout.tsx      # For login/signup
│   │   ├── DashboardLayout.tsx # Main app layout
│   │   └── LandingLayout.tsx   # Marketing site layout
│   ├── pages/                  # Route pages
│   │   ├── landing/
│   │   │   ├── HomePage.tsx
│   │   │   ├── FeaturesPage.tsx
│   │   │   └── PricingPage.tsx
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── ForgotPasswordPage.tsx
│   │   │   └── ResetPasswordPage.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── campaigns/
│   │   │   ├── CampaignsListPage.tsx
│   │   │   ├── CampaignCreatePage.tsx
│   │   │   ├── CampaignDetailPage.tsx
│   │   │   └── CampaignEditPage.tsx
│   │   ├── generation/
│   │   │   ├── GenerateEmailPage.tsx
│   │   │   ├── RefineEmailPage.tsx
│   │   │   └── GenerationHistoryPage.tsx
│   │   ├── profile/
│   │   │   ├── ProfilePage.tsx
│   │   │   └── SettingsPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── store/                  # Zustand stores
│   │   ├── authStore.ts        # Auth state (user, tokens)
│   │   └── uiStore.ts          # UI state (sidebar, theme)
│   ├── types/                  # TypeScript types
│   │   ├── api.types.ts        # API response/request types
│   │   ├── campaign.types.ts   # Campaign models
│   │   ├── user.types.ts       # User models
│   │   └── ai.types.ts         # AI generation types
│   ├── utils/                  # Utility functions
│   │   ├── formatters.ts       # Date, number formatting
│   │   ├── validators.ts       # Zod schemas
│   │   ├── constants.ts        # App constants
│   │   └── helpers.ts          # Helper functions
│   ├── App.tsx                 # Root component
│   ├── main.tsx               # Entry point
│   ├── router.tsx             # Route configuration
│   └── vite-env.d.ts
├── .env.example
├── .env.local
├── .gitignore
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## 3. PAGES & ROUTES

### Public Routes (Unauthenticated)

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | HomePage | Landing page with hero, features, CTA |
| `/features` | FeaturesPage | Detailed feature showcase |
| `/pricing` | PricingPage | Pricing plans |
| `/login` | LoginPage | Login form |
| `/signup` | SignupPage | Registration form |
| `/forgot-password` | ForgotPasswordPage | Request password reset |
| `/reset-password?token=xxx` | ResetPasswordPage | Reset password form |

### Protected Routes (Authenticated)

| Route | Component | Description |
|-------|-----------|-------------|
| `/dashboard` | DashboardPage | Overview, stats, recent campaigns |
| `/campaigns` | CampaignsListPage | All campaigns with filters |
| `/campaigns/new` | CampaignCreatePage | Create new campaign |
| `/campaigns/:id` | CampaignDetailPage | Campaign details & analytics |
| `/campaigns/:id/edit` | CampaignEditPage | Edit campaign |
| `/campaigns/:id/generate` | GenerateEmailPage | AI email generation interface |
| `/campaigns/:id/refine/:templateId` | RefineEmailPage | Refine existing email |
| `/campaigns/:id/history` | GenerationHistoryPage | View all generation jobs |
| `/profile` | ProfilePage | User profile |
| `/settings` | SettingsPage | Account settings, change password |
| `*` | NotFoundPage | 404 page |

---

## 4. FEATURE SPECIFICATIONS BY PAGE

### **4.1 Landing Page (HomePage)**

**Sections:**
1. **Hero Section**
   - Headline: "AI-Powered Email Marketing That Converts"
   - Subheadline: "Generate high-converting email campaigns in minutes with Claude AI"
   - CTA: "Start Free Trial" → `/signup`
   - Demo video/screenshot

2. **Features Section**
   - AI Content Generation
   - Multi-Variant Testing
   - Campaign Management
   - Analytics & Tracking
   - Team Collaboration

3. **How It Works**
   - Step 1: Create Campaign
   - Step 2: Generate with AI
   - Step 3: Review & Send
   - Step 4: Track Results

4. **Social Proof**
   - Customer testimonials
   - Company logos
   - Statistics (emails sent, conversion rate)

5. **Pricing Preview**
   - Brief pricing overview
   - Link to `/pricing`

6. **Footer**
   - Links (About, Contact, Terms, Privacy)
   - Social media links

---

### **4.2 Authentication Pages**

#### **LoginPage** (`/login`)
**Features:**
- Email/password form
- "Remember me" checkbox
- "Forgot password?" link
- Form validation (Zod + React Hook Form)
- Error handling (401 → show error toast)
- Redirect to `/dashboard` on success
- Link to `/signup`

**API Integration:**
- `POST /api/v1/auth/login`
- Store tokens in Zustand + localStorage
- Set axios default headers

#### **SignupPage** (`/signup`)
**Features:**
- Full name, email, password, confirm password
- Organization name (auto-creates organization)
- Password strength indicator
- Terms & conditions checkbox
- Form validation
- Auto-login after signup
- Link to `/login`

**API Integration:**
- `POST /api/v1/auth/register`
- Auto-login on success

#### **ForgotPasswordPage** (`/forgot-password`)
**Features:**
- Email input
- Send reset link button
- Success message: "Check your email for reset link"

**API Integration:**
- `POST /api/v1/auth/forgot-password`

#### **ResetPasswordPage** (`/reset-password?token=xxx`)
**Features:**
- New password + confirm password
- Token validation
- Password strength indicator
- Success → redirect to `/login`

**API Integration:**
- `POST /api/v1/auth/reset-password`

---

### **4.3 Dashboard Page** (`/dashboard`)

**Widgets:**
1. **Stats Overview**
   - Total campaigns
   - Active campaigns
   - Emails sent this month
   - Average open rate

2. **Recent Campaigns**
   - List of 5 most recent campaigns
   - Quick actions: View, Edit, Send

3. **Quick Actions**
   - "Create New Campaign" button
   - "Generate Email" button

4. **Activity Feed**
   - Recent generation jobs
   - Campaign status changes

**API Integration:**
- `GET /api/v1/campaigns/stats`
- `GET /api/v1/campaigns?page=1&per_page=5`

---

### **4.4 Campaigns List Page** (`/campaigns`)

**Features:**
1. **Header**
   - "Create Campaign" button
   - Search bar (search by name/description)
   - Filter dropdown (status, date range)
   - View toggle (grid/list)

2. **Campaign Cards/Rows**
   - Campaign name
   - Status badge (draft, scheduled, sending, sent, paused, archived)
   - Created date
   - Scheduled date (if applicable)
   - Quick actions menu:
     - View details
     - Edit
     - Duplicate
     - Schedule/Send
     - Pause/Resume
     - Archive
     - Delete (confirmation dialog)

3. **Pagination**
   - Page navigation
   - Items per page selector

4. **Empty State**
   - "No campaigns yet" illustration
   - "Create your first campaign" CTA

**API Integration:**
- `GET /api/v1/campaigns?page=1&per_page=20&search=xxx&status=draft`
- `POST /api/v1/campaigns/:id/duplicate`
- `POST /api/v1/campaigns/:id/archive`
- `DELETE /api/v1/campaigns/:id`

---

### **4.5 Campaign Create Page** (`/campaigns/new`)

**Form Sections:**

1. **Basic Information**
   - Campaign name (required)
   - Description
   - Target audience description

2. **Objectives & KPIs** (Dynamic list)
   - Add objective button
   - For each objective:
     - Type (primary/secondary)
     - Description
     - KPI name (e.g., "Click-through rate")
     - Target value (e.g., "5%")
     - Priority (1-5)
   - Remove objective button

3. **Campaign Settings**
   - Status (draft, scheduled)
   - Scheduled date/time (if scheduled)

4. **Actions**
   - "Save as Draft" button
   - "Save & Generate Email" button → redirect to generate page
   - "Cancel" button

**Validation:**
- Campaign name required
- At least one objective required
- Scheduled date must be future

**API Integration:**
- `POST /api/v1/campaigns`
- On success → redirect to `/campaigns/:id` or `/campaigns/:id/generate`

---

### **4.6 Campaign Detail Page** (`/campaigns/:id`)

**Tabs:**

#### **Tab 1: Overview**
- Campaign name, description, status
- Created/updated timestamps
- Target audience
- Edit button → `/campaigns/:id/edit`

#### **Tab 2: Objectives**
- List of all objectives with KPIs
- Progress tracking (if applicable)
- Add/Edit/Delete objectives

#### **Tab 3: Email Content**
- List of generated templates
- Preview email content
- "Generate New Email" button → `/campaigns/:id/generate`
- "Refine Email" button → `/campaigns/:id/refine/:templateId`

#### **Tab 4: Generation History**
- All AI generation jobs
- Job status (pending, processing, completed, failed)
- View results button
- Timestamp & user

#### **Tab 5: Analytics** (Future)
- Email performance metrics
- Open rate, click rate
- Engagement charts

**Actions (Top Bar):**
- Schedule button
- Send Now button
- Pause button (if sending/scheduled)
- Resume button (if paused)
- Cancel button (if scheduled)
- Duplicate button
- Archive button
- Delete button

**API Integration:**
- `GET /api/v1/campaigns/:id`
- `GET /api/v1/campaigns/:id/objectives`
- `POST /api/v1/campaigns/:id/schedule`
- `POST /api/v1/campaigns/:id/send`
- `POST /api/v1/campaigns/:id/pause`
- `POST /api/v1/campaigns/:id/resume`
- `POST /api/v1/campaigns/:id/cancel`

---

### **4.7 Generate Email Page** (`/campaigns/:id/generate`)

**Layout:**

#### **Left Panel: Generation Form**

1. **User Prompt** (Textarea)
   - Placeholder: "Describe the email you want to generate..."
   - Examples button → show example prompts
   - Character counter

2. **Generation Options** (Collapsible)
   - **Tone** (Select)
     - professional, friendly, formal, casual, urgent, enthusiastic
   - **Length** (Radio)
     - Short (~100-150 words)
     - Medium (~200-300 words)
     - Long (~400-500 words)
   - **Personalization Level** (Radio)
     - Low, Medium, High
   - **Number of Variants** (Slider: 1-5)
   - **Creativity/Temperature** (Slider: 0-1)

3. **Context Override** (Textarea, optional)
   - Additional context for AI

4. **Generate Button**
   - Shows loading state during generation
   - Disabled during processing

#### **Right Panel: Results**

1. **Job Status Indicator**
   - Pending: "Queuing your request..."
   - Processing: "AI is generating content..." (animated)
   - Completed: "Generation complete!"
   - Failed: Error message with retry button
   - Cancelled: "Generation cancelled"

2. **Variant Cards** (when completed)
   - For each variant:
     - Subject line (editable)
     - Preview text (editable)
     - HTML content (rendered preview)
     - Confidence score (visual indicator)
     - AI reasoning/notes
     - Actions:
       - "Create Template" button
       - "Copy to clipboard"
       - "View full HTML"
       - "Edit" (opens in editor)

3. **Regenerate Options**
   - "Try different options" button
   - "Generate more variants" button

**Real-time Polling:**
- Poll job status every 2 seconds while processing
- Stop polling when completed/failed/cancelled

**API Integration:**
- `POST /api/v1/campaigns/:id/generate`
- `GET /api/v1/campaigns/:id/generate/:job_id` (polling)
- `POST /api/v1/campaigns/:id/generate/:job_id/create-template`
- `POST /api/v1/campaigns/:id/generate/:job_id/cancel`

---

### **4.8 Refine Email Page** (`/campaigns/:id/refine/:templateId`)

**Features:**

1. **Current Email Preview**
   - Show existing email content
   - Subject, preview, body

2. **Refinement Instructions** (Textarea)
   - Placeholder: "How would you like to improve this email?"
   - Examples:
     - "Make the tone more urgent"
     - "Add social proof"
     - "Shorten by 30%"
     - "Strengthen the CTA"

3. **Quick Refinement Buttons**
   - "Make more urgent"
   - "Add scarcity"
   - "Simplify language"
   - "Enhance CTA"
   - Custom chips for common refinements

4. **Refine Button**
   - Triggers async job
   - Shows job status like generation page

5. **Results Panel**
   - Shows refined version
   - Side-by-side comparison with original
   - Accept/Reject buttons

**API Integration:**
- `GET /api/v1/campaigns/:id` (get template)
- `POST /api/v1/campaigns/:id/templates/:templateId/refine`
- Poll job status

---

### **4.9 Subject Line Generator** (Modal/Drawer)

**Trigger:** Button on generation/refine pages

**Features:**
1. **Style Selection** (Checkboxes)
   - Benefit-driven
   - Question-based
   - Urgency
   - Curiosity
   - Social proof
   - Personalized

2. **Number of variants** (1-10)

3. **Generate Button**

4. **Results List**
   - Each subject line with:
     - Character count
     - Preview on mobile
     - "Use this" button
     - Copy button

**API Integration:**
- `POST /api/v1/campaigns/:id/subject-lines`

---

### **4.10 Profile & Settings**

#### **ProfilePage** (`/profile`)
- Display user info
- Full name (editable)
- Email (read-only)
- Organization name
- Member since date
- "Update Profile" button

**API Integration:**
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me` (if update endpoint exists)

#### **SettingsPage** (`/settings`)
**Sections:**
1. **Change Password**
   - Current password
   - New password
   - Confirm new password
   - "Update Password" button

2. **Organization Settings** (Future)
   - Organization name
   - Members list

3. **Preferences** (Future)
   - Email notifications
   - Theme (light/dark)

**API Integration:**
- `POST /api/v1/auth/change-password`

---

## 5. STATE MANAGEMENT

### Zustand Stores

#### **authStore.ts**
```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (tokens: Tokens, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}
```

#### **uiStore.ts**
```typescript
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

### React Query Keys
```typescript
// campaigns
['campaigns', { page, search, status }]
['campaign', campaignId]
['campaign-stats']
['campaign-objectives', campaignId]

// AI generation
['generation-jobs', campaignId]
['generation-job', jobId]

// auth
['current-user']
```

---

## 6. API CLIENT SETUP

### Axios Instance (`api/client.ts`)
```typescript
// Features:
- Base URL from env variable
- Request interceptor: Add Authorization header
- Response interceptor: Handle 401 (refresh token)
- Automatic token refresh on 401
- Logout on refresh token failure
- Request/response logging (dev mode)
```

### Token Refresh Flow
1. Request fails with 401
2. Interceptor catches error
3. Try to refresh using refresh token
4. If refresh succeeds → retry original request
5. If refresh fails → logout user

---

## 7. FORM VALIDATION (Zod Schemas)

### Examples

```typescript
// Login
loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

// Campaign creation
campaignSchema = z.object({
  name: z.string().min(3).max(200),
  description: z.string().optional(),
  target_audience: z.string().optional(),
  objectives: z.array(objectiveSchema).min(1)
})

// Generation options
generationSchema = z.object({
  user_prompt: z.string().min(10),
  generation_options: z.object({
    tone: z.enum([...]),
    length: z.enum([...]),
    variants_count: z.number().min(1).max(5)
  })
})
```

---

## 8. COMPONENT LIBRARY (shadcn/ui)

**Components to install:**
- Button
- Input, Textarea
- Select, Radio Group, Checkbox
- Card
- Dialog (Modal)
- Dropdown Menu
- Form (with React Hook Form)
- Label
- Badge (for status)
- Tabs
- Table
- Pagination
- Toast (notifications)
- Slider
- Switch
- Accordion
- Alert
- Avatar
- Progress (for generation status)
- Separator
- Sheet (drawer)
- Skeleton (loading states)

---

## 9. RESPONSIVE DESIGN BREAKPOINTS

```typescript
sm: 640px   // Mobile landscape
md: 768px   // Tablet
lg: 1024px  // Desktop
xl: 1280px  // Large desktop
2xl: 1536px // Extra large
```

**Layout Strategy:**
- Mobile-first design
- Hamburger menu on mobile
- Sidebar on desktop
- Stack forms vertically on mobile
- Grid layouts on desktop

---

## 10. ERROR HANDLING

### Global Error Boundary
- Catch React component errors
- Show fallback UI
- Log to error tracking service (Sentry)

### API Error Handling
- Network errors → "Check your connection"
- 400 errors → Show field validation errors
- 401 errors → Redirect to login
- 403 errors → "You don't have permission"
- 404 errors → "Resource not found"
- 500 errors → "Something went wrong, try again"
- Show toast notifications for errors

### Form Errors
- Inline validation
- Error messages below fields
- Highlight invalid fields

---

## 11. LOADING STATES

**Patterns:**
1. **Skeleton loaders** for content
2. **Spinners** for actions (button loading)
3. **Progress bars** for AI generation
4. **Shimmer effects** for cards/lists

**React Query Loading:**
- `isLoading` → skeleton
- `isFetching` → subtle indicator
- `isError` → error state

---

## 12. REAL-TIME FEATURES

### Job Polling (AI Generation)
```typescript
// Use React Query with polling
useQuery({
  queryKey: ['generation-job', jobId],
  queryFn: () => getGenerationJob(jobId),
  refetchInterval: (data) => {
    if (data?.status === 'completed' || data?.status === 'failed') {
      return false; // Stop polling
    }
    return 2000; // Poll every 2 seconds
  }
})
```

---

## 13. ACCESSIBILITY (a11y)

**Requirements:**
- Semantic HTML
- ARIA labels for icons
- Keyboard navigation
- Focus management (modals, forms)
- Screen reader support
- Color contrast (WCAG AA)
- Alt text for images

**Tools:**
- eslint-plugin-jsx-a11y
- @axe-core/react (dev mode)

---

## 14. PERFORMANCE OPTIMIZATION

**Strategies:**
1. **Code splitting** - Lazy load pages
2. **Image optimization** - WebP format, lazy loading
3. **Bundle analysis** - vite-bundle-visualizer
4. **Memoization** - useMemo, useCallback for expensive operations
5. **Virtual scrolling** - For long lists (react-virtual)
6. **Debouncing** - Search inputs, form validation
7. **React Query caching** - Reduce API calls

---

## 15. TESTING STRATEGY

### Unit Tests (Vitest)
- Utility functions
- Form validation schemas
- Custom hooks

### Component Tests (React Testing Library)
- Form submissions
- User interactions
- Conditional rendering

### E2E Tests (Playwright)
- Critical user flows:
  - Signup → Login → Create Campaign → Generate Email → Send
  - Password reset flow
  - Campaign CRUD operations

---

## 16. ENVIRONMENT VARIABLES

```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Arrakis Marketeer
VITE_ENABLE_ANALYTICS=false
```

---

## 17. DEVELOPMENT PHASES

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup (Vite + React + TS)
- [ ] Install dependencies
- [ ] Configure Tailwind + shadcn/ui
- [ ] Setup folder structure
- [ ] API client with interceptors
- [ ] Auth store (Zustand)
- [ ] Router setup

### Phase 2: Authentication (Week 2)
- [ ] Login page
- [ ] Signup page
- [ ] Forgot/Reset password pages
- [ ] Protected routes HOC
- [ ] Token refresh flow

### Phase 3: Landing & Marketing (Week 3)
- [ ] Landing page (hero, features)
- [ ] Pricing page
- [ ] Footer with links

### Phase 4: Dashboard & Campaigns (Week 3-4)
- [ ] Dashboard layout (sidebar, header)
- [ ] Dashboard page
- [ ] Campaigns list page
- [ ] Campaign create/edit forms
- [ ] Campaign detail page
- [ ] Campaign CRUD operations

### Phase 5: AI Generation (Week 5-6)
- [ ] Generate email page
- [ ] Generation form with options
- [ ] Job status polling
- [ ] Variant cards display
- [ ] Create template from variant
- [ ] Refine email page
- [ ] Subject line generator

### Phase 6: Objectives & Advanced (Week 6)
- [ ] Objective manager component
- [ ] CRUD for objectives
- [ ] Generation history page
- [ ] Profile & settings pages

### Phase 7: Polish & Testing (Week 7-8)
- [ ] Error handling & validation
- [ ] Loading states & skeletons
- [ ] Responsive design
- [ ] Accessibility audit
- [ ] Unit tests for critical paths
- [ ] E2E tests for main flows
- [ ] Performance optimization

### Phase 8: Deployment (Week 8)
- [ ] Build configuration
- [ ] Environment setup
- [ ] CI/CD pipeline
- [ ] Deploy to hosting (Vercel/Netlify)

---

## 18. DEPENDENCIES (package.json)

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.22.0",
    "@tanstack/react-query": "^5.28.0",
    "zustand": "^4.5.2",
    "axios": "^1.6.7",
    "react-hook-form": "^7.51.0",
    "@hookform/resolvers": "^3.3.4",
    "zod": "^3.22.4",
    "date-fns": "^3.3.1",
    "react-hot-toast": "^2.4.1",
    "framer-motion": "^11.0.8",
    "lucide-react": "^0.358.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-slider": "^1.1.2"
  },
  "devDependencies": {
    "@types/react": "^18.3.1",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.4.2",
    "vite": "^5.2.0",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35",
    "eslint": "^8.57.0",
    "@typescript-eslint/eslint-plugin": "^7.2.0",
    "@typescript-eslint/parser": "^7.2.0",
    "vitest": "^1.4.0",
    "@testing-library/react": "^14.2.1",
    "@testing-library/jest-dom": "^6.4.2",
    "prettier": "^3.2.5"
  }
}
```

---

## 19. DESIGN SYSTEM

### Color Palette (Tailwind)
```javascript
colors: {
  primary: { /* Main brand color */ },
  secondary: { /* Accent color */ },
  success: { /* Green for success states */ },
  warning: { /* Yellow for warnings */ },
  error: { /* Red for errors */ },
  info: { /* Blue for info */ }
}
```

### Typography
- Headings: Font weight 700
- Body: Font weight 400
- Small text: 14px
- Default: 16px

### Spacing
- Use Tailwind's spacing scale (4px base)

---

## 20. KEY USER FLOWS

### Flow 1: New User Signup → First Campaign
1. Land on homepage
2. Click "Start Free Trial"
3. Fill signup form (name, email, password, org)
4. Auto-login → Redirect to dashboard
5. Click "Create Campaign"
6. Fill campaign form with objectives
7. Click "Save & Generate Email"
8. Fill generation prompt & options
9. Click "Generate"
10. Wait for AI (polling status)
11. Review variants
12. Click "Create Template" on best variant
13. Return to campaign detail
14. Click "Send Now" or "Schedule"

### Flow 2: Refine Existing Email
1. Go to campaign detail
2. Click on email template
3. Click "Refine"
4. Enter refinement instructions
5. Generate → Wait for results
6. Compare original vs refined
7. Accept refined version

### Flow 3: Forgot Password
1. Click "Forgot password?" on login
2. Enter email
3. Check email for reset link
4. Click link (opens reset page)
5. Enter new password
6. Submit → Redirect to login
7. Login with new password

---

## 21. FUTURE ENHANCEMENTS (Post-MVP)

- [ ] Analytics dashboard with charts
- [ ] Email scheduling calendar view
- [ ] A/B testing interface for subject lines
- [ ] Team collaboration (comments, approvals)
- [ ] Organization member management
- [ ] Email template library
- [ ] Custom branding (logo, colors)
- [ ] Integration with email service providers (SendGrid, Mailgun)
- [ ] Contact list management
- [ ] Segmentation for targeted campaigns
- [ ] Dark mode toggle
- [ ] Export campaign reports (PDF/CSV)
- [ ] Webhook configuration
- [ ] API key management

---

## 22. SUCCESS METRICS

**Technical KPIs:**
- Lighthouse score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Bundle size < 500KB (gzipped)
- Test coverage > 70%

**User Experience:**
- Campaign creation < 2 minutes
- Email generation < 30 seconds
- Zero-state to first email sent < 5 minutes

---

## SUMMARY

This plan provides a complete roadmap for building a modern, scalable React TypeScript frontend that integrates with all backend APIs. The architecture emphasizes:

✅ **Type Safety** - Full TypeScript coverage
✅ **Performance** - Code splitting, lazy loading, caching
✅ **User Experience** - Real-time updates, optimistic UI
✅ **Developer Experience** - Clear structure, reusable components
✅ **Maintainability** - Consistent patterns, comprehensive testing
✅ **Accessibility** - WCAG compliance
✅ **Scalability** - Modular architecture

**Estimated Timeline:** 7-8 weeks for full implementation
**Team Size:** 2-3 frontend developers
