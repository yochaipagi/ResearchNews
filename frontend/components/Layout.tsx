import React, { ReactNode } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useSession, signIn, signOut } from 'next-auth/react';
import { 
  HomeIcon, 
  BookmarkIcon, 
  UserIcon,
  BellIcon,
  MagnifyingGlassIcon,
  ArrowRightOnRectangleIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

const Layout: React.FC<LayoutProps> = ({
  children,
  title = 'Research Feed',
}) => {
  const { data: session } = useSession();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Head>
        <title>{title}</title>
        <meta name="description" content="Twitter-like feed of arXiv research papers" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Sidebar navigation */}
      <div className="w-20 md:w-64 bg-white border-r border-gray-200 fixed h-full flex flex-col">
        <div className="p-4">
          <Link href="/" className="flex items-center justify-center md:justify-start">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-xl">R</span>
            </div>
            <span className="ml-2 font-bold text-xl hidden md:block">ResearchFeed</span>
          </Link>
        </div>

        <nav className="mt-6 flex-1">
          <ul>
            <li>
              <Link href="/" className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full mx-2 transition">
                <HomeIcon className="w-6 h-6" />
                <span className="ml-3 hidden md:block">Home</span>
              </Link>
            </li>
            
            <li>
              <Link href="/explore" className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full mx-2 transition">
                <MagnifyingGlassIcon className="w-6 h-6" />
                <span className="ml-3 hidden md:block">Explore</span>
              </Link>
            </li>
            
            <li>
              <Link href="/saved" className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full mx-2 transition">
                <BookmarkIcon className="w-6 h-6" />
                <span className="ml-3 hidden md:block">Saved Papers</span>
              </Link>
            </li>
            
            {session && (
              <>
                <li>
                  <Link href="#" className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full mx-2 transition">
                    <BellIcon className="w-6 h-6" />
                    <span className="ml-3 hidden md:block">Notifications</span>
                  </Link>
                </li>
                <li>
                  <Link href="#" className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full mx-2 transition">
                    <UserIcon className="w-6 h-6" />
                    <span className="ml-3 hidden md:block">Profile</span>
                  </Link>
                </li>
              </>
            )}
            {!session && (
              <li>
                <Link href="/saved" className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full mx-2 transition">
                  <BookmarkIcon className="w-6 h-6" />
                  <span className="ml-3 hidden md:block">Saved Papers</span>
                </Link>
              </li>
            )}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-200">
          {session ? (
            <button
              onClick={() => signOut()}
              className="flex items-center px-4 py-2 w-full text-gray-700 hover:bg-red-50 hover:text-red-600 rounded-full transition"
            >
              <ArrowLeftOnRectangleIcon className="w-6 h-6" />
              <span className="ml-3 hidden md:block">Sign Out</span>
            </button>
          ) : (
            <button
              onClick={() => signIn()}
              className="flex items-center px-4 py-2 w-full text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-full transition"
            >
              <ArrowRightOnRectangleIcon className="w-6 h-6" />
              <span className="ml-3 hidden md:block">Sign In</span>
            </button>
          )}
          
          {session && (
            <div className="mt-4 flex items-center">
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                {session.user?.image ? (
                  <img src={session.user.image} alt={session.user.name || 'User'} className="w-full h-full object-cover" />
                ) : (
                  <UserIcon className="w-6 h-6 text-gray-600" />
                )}
              </div>
              <div className="ml-3 hidden md:block">
                <p className="font-medium text-sm">{session.user?.name || 'User'}</p>
                <p className="text-xs text-gray-500">{session.user?.email}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 ml-20 md:ml-64">
        <div className="max-w-2xl mx-auto py-8 px-4">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout; 