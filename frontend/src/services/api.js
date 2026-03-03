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

export const essayService = {
    getStudentHistory: async (studentId) => {
        const response = await api.get(`/student-history/${studentId}`);
        return response.data;
    },

    getTopicsForStudent: async () => {
        const response = await api.get('/get-topics-student');
        return response.data;
    },
    getTopics: async () => {
        const response = await api.get('/get-topics');
        return response.data;
    },
    submitEssay: async (payload) => {
        const response = await api.post('/submit-essay', payload);
        return response.data;
    },
};

export const teacherService = {
    // This route must exist in your backend and return keywords
    getTopicsForTeacher: async () => {
        const response = await api.get('/get-topics-teacher');
        return response.data;
    },
    addTopic: async (topicData) => {
        const response = await api.post('/add-topic', topicData);
        return response.data;
    },
    deleteTopic: async (topicId) => {
        const response = await api.delete(`/delete-topic/${topicId}`);
        return response.data;
    },
    getSubmissions: async (topicId) => {
        const response = await api.get(`/topic-submissions/${topicId}`);
        return response.data;
    }
};

export default api;