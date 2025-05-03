// firebase.js

// 1) Your Firebase config from the console:
const firebaseConfig = {
  apiKey: "AIzaSyAR4LR4zVtL-6NcfVhOiyyWaZkO9EBnVmA",
  authDomain: "budget-bot-firebase.firebaseapp.com",
  projectId: "budget-bot-firebase",
  storageBucket: "budget-bot-firebase.firebasestorage.app",
  messagingSenderId: "64898674975",
  appId: "1:64898674975:web:388ec00b42d2fc04e8c02a"
};

// 2) Import the Firebase modules as ES modules
//    We use the official 'modular' SDK (v9+).
import { initializeApp } 
  from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getFirestore } 
  from "https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore.js";

// 3) Initialize the app & Firestore
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);

// We'll add more Firestore logic (categories, deposits, transactions) soon.
