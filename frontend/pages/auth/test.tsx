import { useEffect, useState } from 'react';
import { useSession, signIn, signOut } from 'next-auth/react';
import Layout from '../../components/Layout';
import { setAuthToken, clearAuthToken, registerUser } from '../../lib/api';

export default function AuthTest() {
  const { data: session } = useSession();
  const [registeredUser, setRegisteredUser] = useState(null);
  const [error, setError] = useState('');
  const [token, setToken] = useState('');

  useEffect(() => {
    // Check for existing token
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  useEffect(() => {
    const handleRegistration = async () => {
      if (session?.user?.email) {
        try {
          // Register the user in our backend
          const user = await registerUser(session.user.email);
          setRegisteredUser(user);
          
          // Store the email as the auth token (simplified for testing)
          setAuthToken(session.user.email);
          setToken(session.user.email);
        } catch (err) {
          setError('Failed to register user with backend');
          console.error(err);
        }
      }
    };

    if (session) {
      handleRegistration();
    } else {
      setRegisteredUser(null);
      clearAuthToken();
      setToken('');
    }
  }, [session]);

  return (
    <Layout title="Auth Test | Research Feed">
      <div className="max-w-md mx-auto card">
        <h1 className="text-2xl font-bold text-center mb-6">Authentication Test</h1>

        <div className="space-y-4">
          <div className="p-4 bg-gray-100 rounded-md">
            <h2 className="text-lg font-semibold mb-2">Session Status</h2>
            {session ? (
              <div>
                <p className="text-green-600 font-medium">Authenticated</p>
                <p className="mt-2">Signed in as: {session.user?.email}</p>
                {session.user?.image && (
                  <img 
                    src={session.user.image} 
                    className="mt-2 w-12 h-12 rounded-full" 
                    alt={session.user.name || 'User'}
                  />
                )}
              </div>
            ) : (
              <p className="text-red-600 font-medium">Not authenticated</p>
            )}
          </div>

          <div className="p-4 bg-gray-100 rounded-md">
            <h2 className="text-lg font-semibold mb-2">Backend Registration</h2>
            {registeredUser ? (
              <div>
                <p className="text-green-600 font-medium">Registered with backend</p>
                <p className="mt-2">User ID: {registeredUser.id}</p>
                <p>Email: {registeredUser.email}</p>
              </div>
            ) : (
              <p className="text-gray-600">Not registered with backend</p>
            )}
            {error && <p className="text-red-600 mt-2">{error}</p>}
          </div>

          <div className="p-4 bg-gray-100 rounded-md">
            <h2 className="text-lg font-semibold mb-2">Auth Token</h2>
            {token ? (
              <div>
                <p className="text-green-600 font-medium">Token stored</p>
                <p className="mt-2 text-xs break-all">{token}</p>
              </div>
            ) : (
              <p className="text-gray-600">No token stored</p>
            )}
          </div>

          <div className="flex justify-center space-x-4">
            {!session ? (
              <button
                onClick={() => signIn('google')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Sign in with Google
              </button>
            ) : (
              <button
                onClick={() => signOut()}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Sign Out
              </button>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
} 