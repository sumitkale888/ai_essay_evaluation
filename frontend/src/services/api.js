import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    response => response,
    error => {
        // Log error for debugging
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

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
    getStudentClassrooms: async (studentId) => {
        const response = await api.get(`/student/classrooms/${studentId}`);
        return response.data;
    },

    joinClassroom: async (payload) => {
        const response = await api.post('/student/join-classroom', payload);
        return response.data;
    },

    getTopicsForStudent: async (studentId, classroomId = null) => {
        const params = classroomId ? `?classroom_id=${classroomId}` : '';
        const response = await api.get(`/student/get-topics-student/${studentId}${params}`);
        return response.data;
    },

    
    getStudentHistory: async (studentId) => {
        const response = await api.get(`/student/student-history/${studentId}`);
        return response.data;
    },

 
    submitEssay: async (payload) => {
        const response = await api.post('/student/submit-essay', payload);
        return response.data;
    },
    submitEssayAsync: async (payload) => {
        const response = await api.post('/student/submit-essay-async', payload);
        return response.data;
    },
    getTaskStatus: async (taskId) => {
        const response = await api.get(`/student/task-status/${taskId}`);
        return response.data;
    },
    extractEssayText: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/student/extract-essay-text', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },
    submitFileAsync: async (studentId, topicId, file) => {
        const formData = new FormData();
        formData.append('student_id', String(studentId));
        formData.append('topic_id', String(topicId));
        formData.append('file', file);
        const response = await api.post('/student/submit-file-async', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },
    submitFile: async (studentId, topicId, file) => {
        const formData = new FormData();
        formData.append('student_id', String(studentId));
        formData.append('topic_id', String(topicId));
        formData.append('file', file);
        const response = await api.post('/student/submit-file', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },
};

export const teacherService = {
    createClassroom: async (payload) => {
        const response = await api.post('/teacher/create-classroom', payload);
        return response.data;
    },

    getClassrooms: async (teacherId) => {
        const response = await api.get(`/teacher/classrooms/${teacherId}`);
        return response.data;
    },

    deleteClassroom: async (classroomId, teacherId) => {
        const response = await api.delete(`/teacher/delete-classroom/${classroomId}`, {
            params: { teacher_id: teacherId },
        });
        return response.data;
    },

    getTopicsForTeacher: async (teacherId) => {
        const response = await api.get(`/teacher/get-topics-teacher/${teacherId}`);
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
    },
    getAnalytics: async (teacherId) => {
        const response = await api.get(`/teacher/analytics/${teacherId}`);
        return response.data;
    },
    saveSubmissionReview: async (payload) => {
        const response = await api.post('/teacher/review-submission', payload);
        return response.data;
    }
};

export default api;