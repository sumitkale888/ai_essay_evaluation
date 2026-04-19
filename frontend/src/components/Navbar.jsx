import React from 'react';
import { useNavigate, Link, NavLink, useLocation } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const user = JSON.parse(localStorage.getItem('user'));
    const isStudentDashboard = location.pathname === '/student-dashboard';
    const isClassroomsTab = isStudentDashboard && (!location.search || location.search.includes('tab=classrooms'));
    const isPerformanceTab = isStudentDashboard && location.search.includes('tab=performance');

  
    const getHomeLink = () => {
        if (!user) return "/";
        return user.role === 'teacher' ? "/teacher/topics" : "/student-dashboard";
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/');
    };

    return (
        <nav className="sticky top-0 z-20 bg-gradient-to-r from-emerald-700 via-teal-700 to-lime-700 text-white border-b border-emerald-900/20 shadow-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
           
            <Link to={getHomeLink()} className="text-xl font-black tracking-tight text-white">
                AI <span className="text-lime-200">Grader</span>
            </Link>
            
            <div className="flex items-center gap-6">
                {user?.role === 'teacher' && (
                    <div className="flex gap-4 border-r pr-4 border-white/30">
                        <Link to="/teacher/topics" className="text-emerald-50 hover:text-lime-200 font-semibold transition-colors">
                            Classrooms
                        </Link>
                        <Link to="/teacher/analytics" className="text-emerald-50 hover:text-lime-200 font-semibold transition-colors">
                            Analytics
                        </Link>
                    </div>
                )}

                {user?.role === 'student' && (
                    <div className="flex gap-2 border-r pr-4 border-white/30">
                        <NavLink
                            to="/student-dashboard?tab=classrooms"
                            className={() =>
                                `px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                                    isClassroomsTab
                                        ? 'bg-white text-emerald-700'
                                        : 'text-emerald-50 hover:bg-white/20'
                                }`
                            }
                        >
                            Classrooms
                        </NavLink>
                        <NavLink
                            to="/student-dashboard?tab=performance"
                            className={() =>
                                `px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                                    isPerformanceTab
                                        ? 'bg-white text-emerald-700'
                                        : 'text-emerald-50 hover:bg-white/20'
                                }`
                            }
                        >
                            Performance
                        </NavLink>
                    </div>
                )}
                
                {user && (
                    <div className="flex items-center gap-4">
                        <span className="bg-white/20 text-white px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border border-white/30">
                            {user.role}
                        </span>
                        <button 
                            onClick={handleLogout}
                            className="bg-white text-emerald-700 px-4 py-2 rounded-lg hover:bg-emerald-50 transition text-sm font-bold"
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