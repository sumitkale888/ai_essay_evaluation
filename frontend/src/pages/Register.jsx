import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';

const Register = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        role: 'student' // Default role
    });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            await authService.register(formData);
            alert("Registration Successful! Please Login.");
            navigate('/'); // Redirect to login page
        } catch (err) {
            setError(err.response?.data?.detail || "Registration failed. Try again.");
        }
    };

    return (
        <div className="max-w-md mx-auto mt-16 p-8 bg-white rounded-2xl shadow-xl border border-gray-100">
            <h2 className="text-3xl font-black text-center text-gray-800 mb-2">Create Account</h2>
            <p className="text-center text-gray-500 mb-8">Join the AI Assessment Framework</p>
            
            {error && <p className="bg-red-50 text-red-500 p-3 rounded-lg text-center mb-4 text-sm font-medium">{error}</p>}
            
            <form onSubmit={handleRegister} className="space-y-5">
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Full Name</label>
                    <input 
                        name="name" type="text" placeholder="Sumit Kale" required
                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition"
                        onChange={handleChange}
                    />
                </div>

                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Email Address</label>
                    <input 
                        name="email" type="email" placeholder="name@example.com" required
                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition"
                        onChange={handleChange}
                    />
                </div>

                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">Password</label>
                    <input 
                        name="password" type="password" placeholder="••••••••" required
                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition"
                        onChange={handleChange}
                    />
                </div>

                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">I am a...</label>
                    <select 
                        name="role" 
                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none cursor-pointer"
                        onChange={handleChange}
                        value={formData.role}
                    >
                        <option value="student">Student (Submit Essays)</option>
                        <option value="teacher">Teacher (Create Topics)</option>
                    </select>
                </div>

                <button type="submit" className="w-full bg-blue-600 text-white p-4 rounded-xl font-bold text-lg hover:bg-blue-700 transform hover:-translate-y-1 transition shadow-lg shadow-blue-200">
                    Sign Up
                </button>
            </form>

            <p className="text-center mt-6 text-gray-600">
                Already have an account? <Link to="/" className="text-blue-600 font-bold hover:underline">Login</Link>
            </p>
        </div>
    );
};

export default Register;