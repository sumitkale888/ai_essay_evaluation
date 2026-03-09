import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const authService = {
    login: async (email, password) => {
        const response = await api.post('/login', { email, password });
        return response.data;
    },
    register: async (userData) => {
        const response = await api.post('/register', userData);
        return response.data;
    },
};

// src/services/api.js

export const essayService = {
    // This one is working in your logs because you likely added /student
    getTopicsForStudent: async () => {
        const response = await api.get('/student/get-topics-student'); 
        return response.data;
    },

    // FIX THIS: Add /student prefix here
    getStudentHistory: async (studentId) => {
        const response = await api.get(`/student/student-history/${studentId}`);
        return response.data;
    },

    // FIX THIS: Add /student prefix here too
    submitEssay: async (payload) => {
        const response = await api.post('/student/submit-essay', payload);
        return response.data;
    },
};

export const teacherService = {
    // FIXED: Added /teacher prefix to all teacher routes
    getTopicsForTeacher: async () => {
        const response = await api.get('/teacher/get-topics-teacher');
        return response.data;
    },
    addTopic: async (topicData) => {
        const response = await api.post('/teacher/add-topic', topicData);
        return response.data;
    },
    deleteTopic: async (topicId) => {
        const response = await api.delete(`/teacher/delete-topic/${topicId}`);
        return response.data;
    },
    getSubmissions: async (topicId) => {
        const response = await api.get(`/teacher/topic-submissions/${topicId}`);
        return response.data;
    }
};

export default api;