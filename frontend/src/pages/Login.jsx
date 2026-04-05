import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
    e.preventDefault();
    try {
        const data = await authService.login(email, password);
        localStorage.setItem('user', JSON.stringify(data));

       
        if (data.role === 'teacher') {
            navigate('/teacher/topics'); 
        } else {
            navigate('/student-dashboard');
        }
    } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || "Login failed. Please try again.";
        setError(errorMessage);
    }
};

    return (
        <div className="max-w-md mx-auto mt-16 p-8 bg-white/95 rounded-2xl shadow-xl border border-blue-100">
            <div className="h-1.5 w-28 rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 mx-auto mb-6"></div>
            <div className="text-center mb-6">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-500">Welcome Back</p>
                <h2 className="text-3xl font-black text-slate-800 mt-2">AI Essay Grader</h2>
            </div>
            {error && <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}
            <form onSubmit={handleLogin} className="space-y-4">
                <input 
                    type="email" placeholder="Email" required
                    className="w-full p-3 border border-slate-200 bg-slate-50 rounded-xl focus:ring-2 focus:ring-blue-400 outline-none"
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input 
                    type="password" placeholder="Password" required
                    className="w-full p-3 border border-slate-200 bg-slate-50 rounded-xl focus:ring-2 focus:ring-blue-400 outline-none"
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-3 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition shadow-sm">
                    Login
                </button>
            </form>
            
           
            <p className="text-center mt-6 text-slate-600">
                Don't have an account? <Link to="/register" className="text-blue-600 font-bold hover:underline">Register</Link>
            </p>
        </div>
    );
};

export default Login;