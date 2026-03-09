import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('user'));

    // Fix: Dynamic home link based on role
    const getHomeLink = () => {
        if (!user) return "/";
        return user.role === 'teacher' ? "/teacher/topics" : "/student-dashboard";
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/');
    };

    return (
        <nav className="bg-white shadow-md p-4 flex justify-between items-center px-10">
            {/* Logo now points to the correct dashboard */}
            <Link to={getHomeLink()} className="text-xl font-bold text-blue-600">
                AI Grader
            </Link>
            
            <div className="flex items-center gap-6">
                {user?.role === 'teacher' && (
                    <div className="flex gap-4 border-r pr-4 border-gray-200">
                        <Link to="/teacher/create-topic" className="text-gray-600 hover:text-blue-600 font-medium">
                            Add Topic
                        </Link>
                        <Link to="/teacher/topics" className="text-gray-600 hover:text-blue-600 font-medium">
                            Manage Topics
                        </Link>
                    </div>
                )}
                
                {user && (
                    <div className="flex items-center gap-4">
                        <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase">
                            {user.role}
                        </span>
                        <button 
                            onClick={handleLogout}
                            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition text-sm font-bold"
                        >
                            Logout
                        </button>
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;