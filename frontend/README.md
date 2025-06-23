# Research Feed Frontend

The frontend for the Research Feed platform, built with Next.js and Tailwind CSS.

## Features

- Infinitely scrollable feed of arXiv papers
- Paper details with LLM-generated summaries
- User authentication with Google OAuth and email
- Save/unsave papers for later reading
- Responsive design

## Technologies

- Next.js 14
- Tailwind CSS
- NextAuth.js
- SWR for data fetching
- React Infinite Scroll
- TypeScript

## Getting Started

### Development

```bash
# Install dependencies
npm install

# Run the development server
npm run dev
```

The application will be available at http://localhost:3000.

### Environment Variables

Create a `.env.local` file in the frontend directory with the following variables:

```
# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Provider
EMAIL_SERVER=smtp://username:password@smtp.example.com:587
EMAIL_FROM=noreply@researchfeed.app
```

## Docker

The frontend can be run using Docker:

```bash
docker build -t research-feed-frontend .
docker run -p 3000:3000 research-feed-frontend
```

## License

This project is licensed under the MIT License. 