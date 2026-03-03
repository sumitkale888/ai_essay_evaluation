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
                navigate('/teacher-dashboard');
            } else {
                navigate('/student-dashboard');
            }
        } catch (err) {
            setError('Invalid email or password');
        }
    };

    return (
        <div className="max-w-md mx-auto mt-20 p-8 bg-white rounded-xl shadow-lg">
            <h2 className="text-3xl font-bold text-center text-blue-600 mb-6">AI Essay Grader</h2>
            {error && <p className="text-red-500 text-center mb-4">{error}</p>}
            <form onSubmit={handleLogin} className="space-y-4">
                <input 
                    type="email" placeholder="Email" required
                    className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400 outline-none"
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input 
                    type="password" placeholder="Password" required
                    className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400 outline-none"
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit" className="w-full bg-blue-600 text-white p-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                    Login
                </button>
            </form>
            
            {/* This is the part that was causing the error */}
            <p className="text-center mt-6 text-gray-600">
                Don't have an account? <Link to="/register" className="text-blue-600 font-bold hover:underline">Register</Link>
            </p>
        </div>
    );
};

export default Login;