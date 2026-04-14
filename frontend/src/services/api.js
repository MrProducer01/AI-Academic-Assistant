import axios from "axios";
import { supabase } from "../lib/supabaseClient";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");
const API_PREFIX = (import.meta.env.VITE_API_PREFIX || "/api/v1").replace(/\/+$/, "");

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 12000,
});

apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function apiPath(path) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_PREFIX}${normalized}`;
}

function toNumber(value, fallback = 0) {
  const normalized = typeof value === "string" ? value.replace("%", "").trim() : value;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function deriveStatus(attendance, averageMarks) {
  if (attendance >= 90 && averageMarks >= 80) {
    return "Good";
  }
  if (attendance >= 75 && averageMarks >= 60) {
    return "Watch";
  }
  return "Risk";
}

function buildStudentPerformance(avgMarks) {
  const base = clamp(avgMarks, 30, 99);
  return [base - 9, base - 5, base - 2, base, base + 2].map((value) => clamp(Math.round(value), 20, 100));
}

function createFallbackEmail(name) {
  if (!name) {
    return "student@academy.edu";
  }
  return `${name.toLowerCase().replace(/\s+/g, ".")}@academy.edu`;
}

export function normalizeStudent(rawStudent) {
  const attendanceValue = toNumber(rawStudent?.attendance);
  const mathMarks = toNumber(rawStudent?.math_marks);
  const scienceMarks = toNumber(rawStudent?.science_marks);
  const englishMarks = toNumber(rawStudent?.english_marks);
  const averageMarks = (mathMarks + scienceMarks + englishMarks) / 3;
  const status = deriveStatus(attendanceValue, averageMarks);

  return {
    id: String(rawStudent?.id ?? ""),
    name: rawStudent?.name || "Unknown Student",
    email: rawStudent?.email || createFallbackEmail(rawStudent?.name),
    cohort: rawStudent?.cohort || "Academic Program",
    attendance: `${attendanceValue.toFixed(0)}%`,
    attendanceValue,
    math_marks: mathMarks,
    science_marks: scienceMarks,
    english_marks: englishMarks,
    averageMarks: Number(averageMarks.toFixed(1)),
    gpa: Number((averageMarks / 25).toFixed(2)),
    progress: Number(averageMarks.toFixed(0)),
    risk: status === "Good" ? "Low" : status === "Watch" ? "Medium" : "High",
    status,
    sessions: toNumber(rawStudent?.sessions, 0),
    notes: rawStudent?.notes || "Monitor academic consistency and reinforce weak concepts weekly.",
    subjectMarks: [
      { subject: "Mathematics", marks: mathMarks },
      { subject: "Science", marks: scienceMarks },
      { subject: "English", marks: englishMarks },
    ],
    performance: rawStudent?.performance || buildStudentPerformance(averageMarks),
  };
}

export async function fetchStudents() {
  const { data } = await apiClient.get(apiPath("/students"));
  const students = Array.isArray(data?.students) ? data.students : [];
  return students.map(normalizeStudent);
}

export async function fetchStudentById(studentId) {
  const { data } = await apiClient.get(apiPath(`/students/${studentId}`));
  return normalizeStudent(data?.student || {});
}

export async function analyzeStudent(studentId, query) {
  const { data } = await apiClient.post(apiPath("/ai/analyze"), {
    student_id: studentId,
    query,
  });
  return data;
}

export async function analyzeClass() {
  const { data } = await apiClient.post(apiPath("/ai/analyze_class"));
  return data;
}
