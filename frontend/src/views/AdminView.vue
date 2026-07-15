<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const router = useRouter();
const auth_store = useAuthStore();


const stats = ref({
    total_students: 0,
    total_companies: 0,
    total_drives: 0
});


const companies = ref([]);
const students = ref([]);
const drives = ref([]);
const applications = ref([]);


const compSearch = ref('');
const studSearch = ref('');
const appSearch = ref('');


const errorMessage = ref('');
const successMessage = ref('');
const isLoading = ref(true);

const fetchStats = async () => {
    try {
        const res = await fetch('http://127.0.0.1:5000/api/admin/stats', {
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) stats.value = data;
    } catch (e) {
        console.error("Error fetching stats:", e);
    }
};

const fetchCompanies = async () => {
    try {
        const url = `http://127.0.0.1:5000/api/admin/companies?search=${compSearch.value}`;
        const res = await fetch(url, {
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) companies.value = data;
    } catch (e) {
        console.error("Error fetching companies:", e);
    }
};

const fetchStudents = async () => {
    try {
        const url = `http://127.0.0.1:5000/api/admin/students?search=${studSearch.value}`;
        const res = await fetch(url, {
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) students.value = data;
    } catch (e) {
        console.error("Error fetching students:", e);
    }
};

const fetchDrives = async () => {
    try {
        const res = await fetch('http://127.0.0.1:5000/api/drives');
        const data = await res.json();
        if (res.ok) drives.value = data;
    } catch (e) {
        console.error("Error fetching drives:", e);
    }
};

const fetchApplications = async () => {
    try {
        const res = await fetch('http://127.0.0.1:5000/api/applications', {
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) applications.value = data;
    } catch (e) {
        console.error("Error fetching applications:", e);
    }
};

const loadAllData = async () => {
    isLoading.value = true;
    errorMessage.value = '';
    try {
        await Promise.all([
            fetchStats(),
            fetchCompanies(),
            fetchStudents(),
            fetchDrives(),
            fetchApplications()
        ]);
    } catch (error) {
        errorMessage.value = "Failed to load admin dashboard data.";
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    loadAllData();
});


const updateCompanyStatus = async (compId, newStatus) => {
    const actionText = newStatus === 1 ? "approve/activate" : "deactivate/blacklist";
    if (!confirm(`Are you sure you want to ${actionText} this company?`)) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/companies/${compId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message || "Company status updated.");
            fetchCompanies();
            fetchStats();
        } else {
            alert(data.message || "Operation failed.");
        }
    } catch (e) {
        console.error(e);
        alert("A network error occurred.");
    }
};

const deleteCompany = async (compId) => {
    if (!confirm("Are you sure you want to permanently delete this company user and all associated drives/applications? This cannot be undone.")) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/companies/${compId}`, {
            method: 'DELETE',
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message || "Company permanently deleted.");
            fetchCompanies();
            fetchDrives();
            fetchStats();
        } else {
            alert(data.message || "Deletion failed.");
        }
    } catch (e) {
        console.error(e);
        alert("A network error occurred.");
    }
};


const updateStudentStatus = async (studId, newStatus) => {
    const statusNames = { 0: 'Active', 1: 'Placed', 2: 'Blacklisted' };
    const actionText = statusNames[newStatus] || 'update';
    if (!confirm(`Are you sure you want to change this student's status to ${actionText}?`)) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/students/${studId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message || "Student status updated.");
            fetchStudents();
            fetchStats();
        } else {
            alert(data.message || "Operation failed.");
        }
    } catch (e) {
        console.error(e);
        alert("A network error occurred.");
    }
};

const deleteStudent = async (studId) => {
    if (!confirm("Are you sure you want to permanently delete this student user and all applications? This cannot be undone.")) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/students/${studId}`, {
            method: 'DELETE',
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message || "Student permanently deleted.");
            fetchStudents();
            fetchApplications();
            fetchStats();
        } else {
            alert(data.message || "Deletion failed.");
        }
    } catch (e) {
        console.error(e);
        alert("A network error occurred.");
    }
};


const updateDriveStatus = async (driveId, newStatus) => {
    const actionText = newStatus === 1 ? 'approve' : 'reject/end';
    if (!confirm(`Are you sure you want to ${actionText} this placement drive?`)) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/drives/${driveId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message || "Drive status updated successfully.");
            fetchDrives();
            fetchStats();
        } else {
            alert(data.message || "Operation failed.");
        }
    } catch (e) {
        console.error(e);
        alert("A network error occurred.");
    }
};

const deleteDrive = async (driveId) => {
    if (!confirm("Are you sure you want to permanently delete this placement drive? This cannot be undone.")) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/admin/drives/${driveId}`, {
            method: 'DELETE',
            headers: { 'Authorization': auth_store.getAuthToken() || '' }
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message || "Drive deleted successfully.");
            fetchDrives();
            fetchStats();
        } else {
            alert(data.message || "Deletion failed.");
        }
    } catch (e) {
        console.error(e);
        alert("A network error occurred.");
    }
};

const formatDate = (dateStr) => {
    try {
        return new Date(dateStr).toLocaleString();
    } catch (e) {
        return dateStr;
    }
};

const filteredApplications = computed(() => {
    if (!appSearch.value) return applications.value;
    const q = appSearch.value.toLowerCase();
    return applications.value.filter(app => 
        app.student_name.toLowerCase().includes(q) ||
        app.company.toLowerCase().includes(q) ||
        app.job_role.toLowerCase().includes(q)
    );
});
</script>

<template>
    <div class="container mt-5">
        <h2 class="mb-4">Admin Management Dashboard</h2>

        <div v-if="isLoading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading admin portal...</p>
        </div>

        <div v-else>
            <!-- Stats Row -->
            <div class="row mb-5">
                <div class="col-md-4 mb-3">
                    <div class="card bg-primary text-white border-0 shadow-sm">
                        <div class="card-body text-center py-4">
                            <h5 class="card-title text-uppercase mb-2 small">Total Students</h5>
                            <h2 class="display-5 mb-0"><strong>{{ stats.total_students }}</strong></h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card bg-success text-white border-0 shadow-sm">
                        <div class="card-body text-center py-4">
                            <h5 class="card-title text-uppercase mb-2 small">Approved Companies</h5>
                            <h2 class="display-5 mb-0"><strong>{{ stats.total_companies }}</strong></h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card bg-indigo text-white border-0 shadow-sm" style="background-color: #6610f2;">
                        <div class="card-body text-center py-4">
                            <h5 class="card-title text-uppercase mb-2 small">Total Drives</h5>
                            <h2 class="display-5 mb-0"><strong>{{ stats.total_drives }}</strong></h2>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab Navigation -->
            <ul class="nav nav-tabs mb-4" id="adminTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="companies-tab" data-bs-toggle="tab" data-bs-target="#companies-panel" type="button" role="tab">
                        Companies
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="drives-tab" data-bs-toggle="tab" data-bs-target="#drives-panel" type="button" role="tab">
                        Placement Drives
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="students-tab" data-bs-toggle="tab" data-bs-target="#students-panel" type="button" role="tab">
                        Students
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="apps-tab" data-bs-toggle="tab" data-bs-target="#apps-panel" type="button" role="tab">
                        Applications ({{ applications.length }})
                    </button>
                </li>
            </ul>

            <!-- Tab Panels -->
            <div class="tab-content" id="adminTabContent">
                
                <!-- Companies Tab -->
                <div class="tab-pane fade show active" id="companies-panel" role="tabpanel">
                    <div class="d-flex mb-3">
                        <input type="text" class="form-control me-2" placeholder="Search companies by name..." v-model="compSearch" @keyup.enter="fetchCompanies">
                        <button class="btn btn-primary" @click="fetchCompanies">Search</button>
                    </div>
                    
                    <div class="card shadow-sm border-0">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover align-middle mb-0">
                                <thead class="table-dark">
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>HR Contact</th>
                                        <th>Status</th>
                                        <th class="text-center">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="comp in companies" :key="comp.comp_id">
                                        <td>{{ comp.comp_id }}</td>
                                        <td><strong>{{ comp.name }}</strong></td>
                                        <td>{{ comp.email }}</td>
                                        <td>{{ comp.hr_con || '-' }}</td>
                                        <td>
                                            <span v-if="comp.status === 1" class="badge bg-success">Active / Approved</span>
                                            <span v-else class="badge bg-warning text-dark">Pending / Deactivated</span>
                                        </td>
                                        <td class="text-center">
                                            <button v-if="comp.status === 0" class="btn btn-sm btn-success me-2" @click="updateCompanyStatus(comp.comp_id, 1)">
                                                Approve
                                            </button>
                                            <button v-else class="btn btn-sm btn-outline-warning me-2" @click="updateCompanyStatus(comp.comp_id, 0)">
                                                Deactivate
                                            </button>
                                            <button class="btn btn-sm btn-danger" @click="deleteCompany(comp.comp_id)">
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                    <tr v-if="companies.length === 0">
                                        <td colspan="6" class="text-center text-muted py-4">No companies found.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Drives Tab -->
                <div class="tab-pane fade" id="drives-panel" role="tabpanel">
                    <div class="card shadow-sm border-0">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover align-middle mb-0">
                                <thead class="table-dark">
                                    <tr>
                                        <th>ID</th>
                                        <th>Company</th>
                                        <th>Job Role</th>
                                        <th>Eligibility (CGPA / Branch)</th>
                                        <th>CTC</th>
                                        <th>Deadline</th>
                                        <th>Status</th>
                                        <th class="text-center">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="drive in drives" :key="drive.id">
                                        <td>{{ drive.id }}</td>
                                        <td><strong>{{ drive.company_name }}</strong></td>
                                        <td>{{ drive.job_role }}</td>
                                        <td>
                                            <span class="small d-block">CGPA &ge; {{ drive.cgpa_c }}</span>
                                            <span class="small text-muted">{{ Array.isArray(drive.branch_c) ? drive.branch_c.join(', ') : '' }}</span>
                                        </td>
                                        <td>{{ drive.job_ctc }} LPA</td>
                                        <td>{{ formatDate(drive.deadline) }}</td>
                                        <td>
                                            <span v-if="drive.status === 0" class="badge bg-warning text-dark">Pending Approval</span>
                                            <span v-else-if="drive.status === 1" class="badge bg-success">Approved / Active</span>
                                            <span v-else class="badge bg-secondary">Ended</span>
                                        </td>
                                        <td class="text-center">
                                            <div class="btn-group" role="group">
                                                <button v-if="drive.status === 0" class="btn btn-sm btn-success" @click="updateDriveStatus(drive.id, 1)">
                                                    Approve
                                                </button>
                                                <button v-if="drive.status === 1" class="btn btn-sm btn-outline-secondary" @click="updateDriveStatus(drive.id, 2)">
                                                    End / Reject
                                                </button>
                                                <button class="btn btn-sm btn-danger" @click="deleteDrive(drive.id)">
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr v-if="drives.length === 0">
                                        <td colspan="8" class="text-center text-muted py-4">No placement drives found.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Students Tab -->
                <div class="tab-pane fade" id="students-panel" role="tabpanel">
                    <div class="d-flex mb-3">
                        <input type="text" class="form-control me-2" placeholder="Search students by name..." v-model="studSearch" @keyup.enter="fetchStudents">
                        <button class="btn btn-primary" @click="fetchStudents">Search</button>
                    </div>

                    <div class="card shadow-sm border-0">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover align-middle mb-0">
                                <thead class="table-dark">
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Branch</th>
                                        <th>CGPA</th>
                                        <th>Status</th>
                                        <th class="text-center">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="stud in students" :key="stud.stud_id">
                                        <td>{{ stud.stud_id }}</td>
                                        <td><strong>{{ stud.name }}</strong></td>
                                        <td>{{ stud.branch }}</td>
                                        <td>{{ stud.cgpa }}</td>
                                        <td>
                                            <span v-if="stud.status === 0" class="badge bg-primary">Active</span>
                                            <span v-else-if="stud.status === 1" class="badge bg-success">Placed</span>
                                            <span v-else-if="stud.status === 2" class="badge bg-danger">Blacklisted</span>
                                        </td>
                                        <td class="text-center">
                                            <div class="btn-group" role="group">
                                                <button v-if="stud.status !== 2" class="btn btn-sm btn-outline-danger" @click="updateStudentStatus(stud.stud_id, 2)">
                                                    Blacklist
                                                </button>
                                                <button v-else class="btn btn-sm btn-success" @click="updateStudentStatus(stud.stud_id, 0)">
                                                    Activate
                                                </button>
                                                <button class="btn btn-sm btn-danger" @click="deleteStudent(stud.stud_id)">
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr v-if="students.length === 0">
                                        <td colspan="6" class="text-center text-muted py-4">No students found.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Applications Tab -->
                <div class="tab-pane fade" id="apps-panel" role="tabpanel">
                    <div class="d-flex mb-3">
                        <input type="text" class="form-control me-2" placeholder="Search applications by student, company, or role..." v-model="appSearch">
                    </div>

                    <div class="card shadow-sm border-0">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover align-middle mb-0">
                                <thead class="table-dark">
                                    <tr>
                                        <th>App ID</th>
                                        <th>Student Name</th>
                                        <th>Student Email</th>
                                        <th>Company</th>
                                        <th>Job Role</th>
                                        <th>Applied At</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="app in filteredApplications" :key="app.app_id">
                                        <td>{{ app.app_id }}</td>
                                        <td><strong>{{ app.student_name }}</strong></td>
                                        <td>{{ app.student_email }}</td>
                                        <td>{{ app.company }}</td>
                                        <td>{{ app.job_role }}</td>
                                        <td>{{ formatDate(app.applied_at) }}</td>
                                        <td>
                                            <span v-if="app.status === 0" class="badge bg-secondary">Applied</span>
                                            <span v-else-if="app.status === 1" class="badge bg-info text-dark">Shortlisted</span>
                                            <span v-else-if="app.status === 2" class="badge bg-success">Accepted</span>
                                            <span v-else-if="app.status === 3" class="badge bg-danger">Rejected</span>
                                        </td>
                                    </tr>
                                    <tr v-if="filteredApplications.length === 0">
                                        <td colspan="7" class="text-center text-muted py-4">No applications found.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>
