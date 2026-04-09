import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem('user'));

  
    const getHomeLink = () => {
        if (!user) return "/";
        return user.role === 'teacher' ? "/teacher/topics" : "/student-dashboard";
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/');
    };

    return (
        <nav className="sticky top-0 z-20 bg-gradient-to-r from-blue-700 via-indigo-700 to-cyan-700 text-white border-b border-blue-900/20 shadow-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
           
            <Link to={getHomeLink()} className="text-xl font-black tracking-tight text-white">
                AI <span className="text-cyan-200">Grader</span>
            </Link>
            
            <div className="flex items-center gap-6">
                {user?.role === 'teacher' && (
                    <div className="flex gap-4 border-r pr-4 border-white/30">
                        <Link to="/teacher/topics" className="text-blue-50 hover:text-cyan-200 font-semibold transition-colors">
                            Classrooms
                        </Link>
                    </div>
                )}
                
                {user && (
                    <div className="flex items-center gap-4">
                        <span className="bg-white/20 text-white px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border border-white/30">
                            {user.role}
                        </span>
                        <button 
                            onClick={handleLogout}
                            className="bg-white text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-50 transition text-sm font-bold"
                        >
                            Logout
                        </button>
                    </div>
                )}
            </div>
            </div>
        </nav>
    );
};

export default Navbar;