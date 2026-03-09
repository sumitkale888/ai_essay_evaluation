import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'; // Added Navigate
import Login from './pages/Login';
import Register from './pages/Register';
import StudentDashboard from './pages/StudentDashboard';
import SubmitEssay from './pages/SubmitEssay';
import ResultView from './pages/ResultView';
import Navbar from './components/Navbar';

// NEW TEACHER PAGES
import CreateTopic from './pages/CreateTopic';
import ExistingTopics from './pages/ExistingTopics';
import StudentSubmissions from './pages/StudentSubmissions';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <Routes>
            {/* Auth Routes */}
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Student Routes */}
            <Route path="/student-dashboard" element={<StudentDashboard />} />
            <Route path="/submit/:topicId" element={<SubmitEssay />} />
            <Route path="/result" element={<ResultView />} />

            {/* Teacher Routes (Separated) */}
            <Route path="/teacher/create-topic" element={<CreateTopic />} />
            <Route path="/teacher/topics" element={<ExistingTopics />} />
            <Route path="/teacher/submissions/:topicId" element={<StudentSubmissions />} />
            
            {/* Redirects to prevent blank pages or handle old links */}
            <Route path="/teacher-dashboard" element={<Navigate to="/teacher/topics" />} />
            <Route path="/teacher" element={<Navigate to="/teacher/topics" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;