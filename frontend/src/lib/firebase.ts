import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyA8bIraGpvVsHWCDWOvDRbeTEzQd8ozQcw",
  authDomain: "digitnew-b8313.firebaseapp.com",
  projectId: "digitnew-b8313",
  storageBucket: "digitnew-b8313.firebasestorage.app",
  messagingSenderId: "751643740815",
  appId: "1:751643740815:web:74360e0ca824caed097efa",
  measurementId: "G-LJZZYZVLH9",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
