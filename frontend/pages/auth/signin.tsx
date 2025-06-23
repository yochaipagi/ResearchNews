import { getCsrfToken, getProviders, signIn } from 'next-auth/react';
import { GetServerSideProps } from 'next';
import Layout from '../../components/Layout';

interface SignInProps {
  csrfToken: string;
  providers: Record<string, any>;
}

export default function SignIn({ csrfToken, providers }: SignInProps) {
  return (
    <Layout title="Sign In | Research Feed">
      <div className="max-w-md mx-auto card">
        <h1 className="text-2xl font-bold text-center mb-6">Sign In</h1>
        
        <div className="space-y-4">
          {/* Email Sign In */}
          <form method="post" action="/api/auth/signin/email">
            <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
            <div className="mb-3">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                className="w-full p-2 border border-gray-300 rounded-md"
                placeholder="your.email@example.com"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full btn btn-primary mb-4"
            >
              Sign in with Email
            </button>
          </form>
          
          {/* OAuth Providers */}
          {Object.values(providers || {})
            .filter((provider: any) => provider.id !== 'email')
            .map((provider: any) => (
              <div key={provider.id}>
                <button
                  onClick={() => signIn(provider.id)}
                  className="w-full btn btn-secondary flex items-center justify-center"
                >
                  <span>Sign in with {provider.name}</span>
                </button>
              </div>
            ))
          }
        </div>
      </div>
    </Layout>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  return {
    props: {
      csrfToken: await getCsrfToken(context) || '',
      providers: await getProviders() || {},
    },
  };
}; 