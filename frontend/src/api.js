import axios from 'axios';

const api = axios.create({
    baseURL: "http://localhost:8000"
});

//Export the Axios instance
export default api;