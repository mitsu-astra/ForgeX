# Industrial AI - Frontend

Next.js 14 frontend for the Visual Inspection & Defect Root-Cause Assistant.

## Features

✅ Complete dashboard with 7 main pages
✅ Responsive design with Tailwind CSS
✅ State management with Zustand
✅ Modern UI with Lucide icons
✅ Type-safe with TypeScript

## Pages

1. **Home** (`/`) - Landing page with overview
2. **Dashboard** (`/dashboard`) - KPIs, recent batches, bottlenecks
3. **Upload** (`/dashboard/upload`) - Multi-format file upload (images, CSVs, ZIP)
4. **Quality** (`/dashboard/quality`) - Defect inspection results grid
5. **Process** (`/dashboard/process`) - Station utilization and bottlenecks
6. **Analysis** (`/dashboard/analysis`) - Root cause correlation analysis
7. **Simulator** (`/dashboard/simulator`) - What-if parameter testing
8. **AI Copilot** (`/dashboard/copilot`) - Natural language Q&A interface
9. **Settings** (`/dashboard/settings`) - User preferences

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Icons**: Lucide React
- **HTTP**: Axios (ready for backend integration)

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page
│   ├── globals.css             # Global styles
│   └── dashboard/
│       ├── layout.tsx          # Dashboard layout with sidebar
│       ├── page.tsx            # Dashboard home
│       ├── upload/page.tsx     # Upload page
│       ├── quality/page.tsx    # Quality monitoring
│       ├── process/page.tsx    # Process health
│       ├── analysis/page.tsx   # Root cause analysis
│       ├── simulator/page.tsx  # What-if simulator
│       ├── copilot/page.tsx    # AI Copilot
│       └── settings/page.tsx   # Settings
├── components/
│   ├── Sidebar.tsx             # Navigation sidebar
│   └── Header.tsx              # Dashboard header
└── lib/
    ├── utils.ts                # Utility functions
    └── store.ts                # Zustand store

```

## Backend Integration

Currently using mock data. To integrate with backend:

1. Update API base URL in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. Create API client in `lib/api.ts`

3. Replace mock data with actual API calls

## Design Features

- **Consistent Navigation**: Sidebar with active state indicators
- **Responsive Grid Layouts**: Works on desktop, tablet, and mobile
- **Color-Coded Status**: Visual indicators for defects, bottlenecks, severity
- **Interactive Components**: Drag-and-drop upload, sliders, real-time updates
- **Dark Mode Ready**: Structure supports theme switching (can be added)

## Notes

- All pages are fully navigable
- File upload works but doesn't process (needs backend)
- Charts/graphs are placeholders (ready for real data)
- All UI components are reusable and well-structured
