import api from "./axiosClient";

export const getSettings = async () => {
  const res = await api.get("/settings");
  return res.data;
};

export const updateSettings = async (payload) => {
  const res = await api.put("/settings", payload);
  return res.data;
};

export const getTodaySchedule = async () => {
  const res = await api.get("/schedule/today");
  return res.data;
};

export const getSchedule = async () => {
    const res = await api.get("/schedule");
    return res.data;
};
  
export const addScheduleEntry = async (data) => {
    const res = await api.post("/schedule", data);
    return res.data;
};
  
export const deleteScheduleEntry = async (id) => {
    const res = await api.delete(`/schedule/${id}`);
    return res.data;
};

export const replaceSchedule = async (entries) => {
    const res = await api.put("/schedule", entries);
    return res.data;
};
