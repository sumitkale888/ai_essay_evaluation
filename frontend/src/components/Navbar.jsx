import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('user'));

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/');
    };

    return (
        <nav className="bg-white shadow-md p-4 flex justify-between items-center px-10">
            <Link to="/" className="text-xl font-bold text-blue-600">AI Grader</Link>
            {user && (
                <div className="flex items-center gap-4">
                    <span className="text-gray-600 font-medium">{user.role.toUpperCase()}</span>
                    <button 
                        onClick={handleLogout}
                        className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                    >
                        Logout
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;