import { initializeApp } from "firebase/app";
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
    apiKey: "AIzaSyCW5tQePdcbk_AlVsj9uUTHKaIxOTKCQss",
    authDomain: "fir-29b8a.firebaseapp.com",
    projectId: "fir-29b8a",
    storageBucket: "fir-29b8a.appspot.com",
    messagingSenderId: "296775505246",
    appId: "1:296775505246:web:22ce75d8dbeb7bf7f82bcf"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
