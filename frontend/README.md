# Graduate Study Abroad Scholarship Search and Application Support System

A comprehensive web application built with **ReactJS**, **Tailwind CSS**, and **Ant Design** components to help students discover, apply for, and manage graduate study abroad scholarships with AI-powered matching and application support.

## 🎯 Features

### Core Functionality
- **Smart Scholarship Discovery**: AI-powered matching based on academic profile and preferences
- **Onboarding Wizard**: Step-by-step profile creation with CV parsing
- **Profile & CV Manager**: Comprehensive profile management with document handling
- **Application Tracker**: Kanban-style progress tracking with deadline management
- **Calendar System**: Integrated deadline and reminder management
- **Document Assistant**: Grammar checking and SOP templates

### Key Capabilities
- **Hard/Soft Condition Matching**: Precise eligibility filtering with weighted scoring
- **RAG-based Recommendations**: Intelligent scholarship ranking and suggestions
- **Progress Monitoring**: Real-time application status tracking
- **Deadline Alerts**: Smart notification system for important dates
- **Mobile-First Design**: Fully responsive across all devices

## 🛠️ Technology Stack

- **Frontend**: React 18+ with Next.js App Router
- **Styling**: Tailwind CSS v4 with custom design tokens
- **UI Components**: Ant Design + shadcn/ui components
- **State Management**: React hooks with SWR for data fetching
- **Icons**: Lucide React
- **TypeScript**: Full type safety throughout

## 📋 Prerequisites

Before running this project, ensure you have:

- **Node.js** (version 18.0 or higher)
- **npm** or **yarn** package manager
- **Git** for version control

## 🚀 Getting Started

### 1. Clone the Repository

\`\`\`bash
git clone <repository-url>
cd scholarship-search-app
\`\`\`

### 2. Install Dependencies

Using npm:
\`\`\`bash
npm install
\`\`\`

Using yarn:
\`\`\`bash
yarn install
\`\`\`

### 3. Environment Setup

Create a `.env.local` file in the root directory:

\`\`\`env
# Application Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME="ScholarSearch"

# API Configuration (if using external APIs)
# NEXT_PUBLIC_API_URL=your-api-url
# API_SECRET_KEY=your-secret-key

# Database Configuration (if using database)
# DATABASE_URL=your-database-url

# Authentication (if implementing auth)
# NEXTAUTH_SECRET=your-nextauth-secret
# NEXTAUTH_URL=http://localhost:3000
\`\`\`

### 4. Run the Development Server

\`\`\`bash
npm run dev
# or
yarn dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### 5. Build for Production

\`\`\`bash
npm run build
npm start
# or
yarn build
yarn start
\`\`\`

## 📁 Project Structure

\`\`\`
scholarship-search-app/
├── app/                          # Next.js App Router pages
│   ├── applications/            # Application management pages
│   ├── calendar/               # Deadline calendar pages
│   ├── onboarding/             # User onboarding flow
│   ├── profile/                # Profile management pages
│   ├── scholarships/           # Scholarship discovery pages
│   ├── globals.css             # Global styles and design tokens
│   ├── layout.tsx              # Root layout component
│   └── App.tsx                 # Homepage
├── components/                  # Reusable React components
│   ├── applications/           # Application-related components
│   ├── calendar/               # Calendar and deadline components
│   ├── layout/                 # Layout components (header, sidebar)
│   ├── onboarding/             # Onboarding wizard components
│   ├── profile/                # Profile management components
│   ├── scholarships/           # Scholarship discovery components
│   └── ui/                     # Base UI components (shadcn/ui)
├── hooks/                      # Custom React hooks
├── lib/                        # Utility functions and configurations
├── public/                     # Static assets
└── types/                      # TypeScript type definitions
\`\`\`

## 🎨 Design System

The application uses a custom design system built on Tailwind CSS v4:

### Color Palette
- **Primary**: Academic blue (#1e40af) for trust and professionalism
- **Secondary**: Warm amber (#f59e0b) for highlights and CTAs
- **Success**: Forest green (#059669) for positive states
- **Warning**: Orange (#ea580c) for urgent deadlines
- **Neutrals**: Sophisticated grays for text and backgrounds

### Typography
- **Headings**: Inter font family with balanced line heights
- **Body**: System font stack for optimal readability
- **Responsive scaling**: Mobile-first approach with progressive enhancement

### Components
- **Touch-friendly**: Minimum 44px touch targets for mobile
- **Accessible**: WCAG 2.1 AA compliant with proper ARIA labels
- **Responsive**: Breakpoints at 640px, 768px, 1024px, and 1280px

## 📱 Responsive Design

The application is built mobile-first with specific optimizations:

### Mobile (< 768px)
- Stacked layouts with full-width components
- Bottom sheet modals instead of desktop modals
- Collapsible navigation with hamburger menu
- Touch-optimized button sizes and spacing

### Tablet (768px - 1024px)
- Two-column layouts where appropriate
- Adaptive grid systems
- Optimized for both portrait and landscape

### Desktop (> 1024px)
- Multi-column layouts with sidebar navigation
- Drag-and-drop functionality in Kanban boards
- Hover states and advanced interactions

## 🔧 Key Components

### Onboarding Wizard (`/onboarding`)
- 5-step profile creation process
- CV upload and parsing functionality
- Form validation and progress tracking
- Academic background and test score collection

### Scholarship Discovery (`/scholarships`)
- AI-powered search and filtering
- Hard/soft condition matching
- Match score calculation and display
- Saved scholarships management

### Application Tracker (`/applications`)
- Kanban board with drag-and-drop (desktop)
- Mobile-optimized card layouts
- Document upload and progress tracking
- Timeline and reminder management

### Profile Manager (`/profile`)
- Tabbed interface for different profile sections
- Real-time form validation
- Document management system
- CV parsing and field extraction

## 🧪 Development Guidelines

### Code Style
- Use TypeScript for all components
- Follow React best practices with hooks
- Implement proper error boundaries
- Use semantic HTML elements

### Performance
- Lazy load components where appropriate
- Optimize images with Next.js Image component
- Implement proper caching strategies
- Use SWR for efficient data fetching

### Accessibility
- Include proper ARIA labels and roles
- Ensure keyboard navigation support
- Maintain color contrast ratios
- Provide screen reader friendly content

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Manual Deployment
\`\`\`bash
npm run build
npm run export  # For static export if needed
\`\`\`

### Docker Deployment
\`\`\`dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
\`\`\`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow
- Follow conventional commit messages
- Ensure all tests pass before submitting PR
- Update documentation for new features
- Maintain responsive design principles

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the component examples in Storybook (if available)

## 🔮 Future Enhancements

- [ ] Real-time notifications with WebSocket
- [ ] Advanced analytics dashboard
- [ ] Integration with university APIs
- [ ] Multi-language support
- [ ] Offline functionality with PWA
- [ ] AI-powered SOP writing assistant
- [ ] Video interview preparation tools
- [ ] Scholarship recommendation engine improvements

---

**Built with ❤️ for students pursuing their dreams of studying abroad**
