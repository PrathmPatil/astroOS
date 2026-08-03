import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

const googleConfigured =
  Boolean(process.env.AUTH_GOOGLE_ID) && Boolean(process.env.AUTH_GOOGLE_SECRET);

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: googleConfigured
    ? [
        Google({
          clientId: process.env.AUTH_GOOGLE_ID!,
          clientSecret: process.env.AUTH_GOOGLE_SECRET!,
        }),
      ]
    : [],
  session: { strategy: "jwt" },
  pages: {
    signIn: "/",
  },
  trustHost: true,
  secret: process.env.AUTH_SECRET,
});

export const isGoogleAuthConfigured = googleConfigured;
