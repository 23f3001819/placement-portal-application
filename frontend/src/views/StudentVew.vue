<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const router = useRouter();
const auth_store = useAuthStore();

const studentProfile = ref(null);
const ongoingDrives = ref([]);
const myApplications = ref([]);
const errorMessage = ref('');
const isLoading = ref(true);

const fetchStudentData = async () => {
    try {
        isLoading.value = true;
        
        
        const profileRes = await fetch('http://127.0.0.1:5000/api/student/profile', {
            method: 'GET',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const profileData = await profileRes.json();
        
        if (!profileRes.ok) {
            errorMessage.value = profileData.message || "Failed to load student profile.";
            isLoading.value = false;
            return;
        }
        
        studentProfile.value = profileData;
        
        
        if (studentProfile.value.status === 2) {
            isLoading.value = false;
            return;
        }

        
        const drivesRes = await fetch('http://127.0.0.1:5000/api/drives', {
            method: 'GET'
        });
        const drivesData = await drivesRes.json();
        
        if (drivesRes.ok) {
            
            const now = new Date();
            ongoingDrives.value = drivesData.filter(d => d.status === 1 && new Date(d.deadline) > now);
        }

        
        const appsRes = await fetch('http://127.0.0.1:5000/api/applications', {
            method: 'GET',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const appsData = await appsRes.json();
        if (appsRes.ok) {
            myApplications.value = appsData;
        }
    } catch (error) {
        console.error("Error loading student dashboard:", error);
        errorMessage.value = "Failed to load dashboard due to a network error.";
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchStudentData();
});

const isEligible = (drive) => {
    if (!studentProfile.value || !drive) return false;
    const cgpaOk = studentProfile.value.cgpa >= (drive.cgpa_c || 0);
    const branches = Array.isArray(drive.branch_c) ? drive.branch_c : [];
    const branchOk = branches.includes(studentProfile.value.branch) || branches.includes('ALL');
    return cgpaOk && branchOk;
};

const hasApplied = (driveId) => {
    return myApplications.value.some(app => app.drive_id === driveId);
};

const applyToDrive = async (driveId) => {
    if (!confirm("Are you sure you want to apply to this placement drive?")) {
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/applications/${driveId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.message || "Applied successfully!");
            fetchStudentData();
        } else {
            alert(data.message || "Failed to apply.");
        }
    } catch (error) {
        console.error("Error applying to drive:", error);
        alert("A network error occurred.");
    }
};

const withdrawApplication = async (driveId) => {
    if (!confirm("Are you sure you want to withdraw this application? This action cannot be undone.")) {
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/applications/${driveId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.message || "Application withdrawn successfully.");
            fetchStudentData();
        } else {
            alert(data.message || "Failed to withdraw application.");
        }
    } catch (error) {
        console.error("Error withdrawing application:", error);
        alert("A network error occurred.");
    }
};

const isExporting = ref(false);

const exportApplications = async () => {
    try {
        isExporting.value = true;
        const response = await fetch('http://127.0.0.1:5000/api/student/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.message || "Export started successfully. Check your email!");
        } else {
            alert(data.message || "Failed to start export.");
        }
    } catch (error) {
        console.error("Error exporting applications:", error);
        alert("A network error occurred.");
    } finally {
        isExporting.value = false;
    }
};

const formatDate = (dateStr) => {
    try {
        return new Date(dateStr).toLocaleString();
    } catch (e) {
        return dateStr;
    }
};
</script>

<template>
    <div class="container mt-5">
        <h2 class="mb-4">Student Placement Dashboard</h2>

        <div v-if="isLoading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading your placement dashboard...</p>
        </div>

        <div v-else>
            <!-- Blacklist warning -->
            <div v-if="studentProfile && studentProfile.status === 2" class="alert alert-danger py-5 text-center">
                <h4 class="alert-heading mb-3"><i class="bi bi-x-octagon-fill me-2"></i>Access Suspended</h4>
                <p class="mb-0">Your account has been blacklisted by the Admin. You cannot view ongoing placement drives or apply to any job openings.</p>
                <p class="text-muted mt-2">Please contact the Placement Office for further details.</p>
            </div>

            <div v-else>
                <!-- Student Details Summary -->
                <div class="card mb-4 bg-light border-0 shadow-sm">
                    <div class="card-body py-3 px-4 d-flex flex-wrap justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-1"><strong>Welcome, {{ studentProfile?.name }}</strong></h5>
                            <span class="text-muted small">Branch: {{ studentProfile?.branch }} | CGPA: {{ studentProfile?.cgpa }}</span>
                        </div>
                        <div class="mt-2 mt-md-0">
                            <span v-if="studentProfile?.status === 1" class="badge bg-success px-3 py-2 fs-6">
                                <i class="bi bi-check-circle-fill me-1"></i>Placed / Selected
                            </span>
                            <span v-else class="badge bg-info text-dark px-3 py-2 fs-6">
                                <i class="bi bi-person-fill-check me-1"></i>Actively Seeking
                            </span>
                        </div>
                    </div>
                </div>

                <div v-if="errorMessage" class="alert alert-danger">
                    {{ errorMessage }}
                </div>

                <!-- Tabs -->
                <ul class="nav nav-tabs mb-4" id="studentTab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="ongoing-tab" data-bs-toggle="tab" data-bs-target="#ongoing" type="button" role="tab" aria-controls="ongoing" aria-selected="true">
                            Ongoing Placement Drives
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="applications-tab" data-bs-toggle="tab" data-bs-target="#applications" type="button" role="tab" aria-controls="applications" aria-selected="false">
                            My Applications ({{ myApplications.length }})
                        </button>
                    </li>
                </ul>

                <div class="tab-content" id="studentTabContent">
                    <!-- Ongoing Drives -->
                    <div class="tab-pane fade show active" id="ongoing" role="tabpanel" aria-labelledby="ongoing-tab">
                        <div class="row">
                            <div class="col-12" v-for="drive in ongoingDrives" :key="drive.id">
                                <div class="card mb-3 shadow-sm border-start border-4" :class="isEligible(drive) ? 'border-primary' : 'border-warning'">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-start flex-wrap">
                                            <div>
                                                <h4 class="card-title text-primary mb-1">{{ drive.job_role }}</h4>
                                                <h5 class="text-secondary mb-3">{{ drive.company_name }}</h5>
                                                
                                                <p class="card-text text-muted">{{ drive.job_desc || 'No job description provided.' }}</p>
                                                
                                                <div class="d-flex flex-wrap gap-3 mb-3">
                                                    <span class="text-dark"><i class="bi bi-cash-stack me-1"></i><strong>CTC:</strong> {{ drive.job_pay }} LPA</span>
                                                    <span class="text-dark"><i class="bi bi-clock me-1"></i><strong>Deadline:</strong> {{ formatDate(drive.deadline) }}</span>
                                                </div>

                                                <div class="bg-light p-2 rounded-2 small mb-3">
                                                    <strong>Eligibility Criteria:</strong>
                                                    <div class="mt-1">
                                                        <span class="me-3">
                                                            Min CGPA: <strong>{{ drive.cgpa_c }}</strong>
                                                            <i v-if="studentProfile?.cgpa >= drive.cgpa_c" class="bi bi-check-circle-fill text-success ms-1"></i>
                                                            <i v-else class="bi bi-x-circle-fill text-danger ms-1"></i>
                                                        </span>
                                                        <span>
                                                            Eligible Branches: <strong>{{ Array.isArray(drive.branch_c) ? drive.branch_c.join(', ') : '' }}</strong>
                                                            <i v-if="Array.isArray(drive.branch_c) && (drive.branch_c.includes(studentProfile?.branch) || drive.branch_c.includes('ALL'))" class="bi bi-check-circle-fill text-success ms-1"></i>
                                                            <i v-else class="bi bi-x-circle-fill text-danger ms-1"></i>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="text-end">
                                                <span v-if="hasApplied(drive.id)" class="badge bg-secondary p-2 mb-2 d-block">Applied</span>
                                                <span v-else-if="studentProfile?.status === 1" class="badge bg-warning text-dark p-2 mb-2 d-block">Already Placed</span>
                                                <button v-else-if="isEligible(drive)" class="btn btn-primary" @click="applyToDrive(drive.id)">
                                                    Apply Now
                                                </button>
                                                <button v-else class="btn btn-outline-warning" disabled>
                                                    Not Eligible
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div v-if="ongoingDrives.length === 0" class="text-center py-5 text-muted">
                                <i class="bi bi-briefcase fs-1 mb-2 d-block"></i>
                                No active placement drives are currently available.
                            </div>
                        </div>
                    </div>

                    <!-- My Applications -->
                    <div class="tab-pane fade" id="applications" role="tabpanel" aria-labelledby="applications-tab">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4 class="mb-0 text-secondary">My Applications</h4>
                            <button class="btn btn-success" @click="exportApplications" :disabled="isExporting">
                                <i class="bi bi-file-earmark-spreadsheet-fill me-1"></i>
                                {{ isExporting ? 'Exporting...' : 'Export Applications as CSV' }}
                            </button>
                        </div>
                        <div class="card shadow-sm border-0">
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-striped table-hover align-middle mb-0">
                                        <thead class="table-dark">
                                            <tr>
                                                <th>Company</th>
                                                <th>Job Role</th>
                                                <th>Applied At</th>
                                                <th>Status</th>
                                                <th class="text-center">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="app in myApplications" :key="app.app_id">
                                                <td><strong>{{ app.company }}</strong></td>
                                                <td>{{ app.job_role }}</td>
                                                <td>{{ formatDate(app.applied_at) }}</td>
                                                <td>
                                                    <span v-if="app.status === 0" class="badge bg-secondary">Applied</span>
                                                    <span v-else-if="app.status === 1" class="badge bg-info text-dark">Shortlisted</span>
                                                    <span v-else-if="app.status === 2" class="badge bg-success">Accepted / Placed</span>
                                                    <span v-else-if="app.status === 3" class="badge bg-danger">Rejected</span>
                                                    <span v-else class="badge bg-light text-dark">Unknown ({{ app.status }})</span>
                                                </td>
                                                <td class="text-center">
                                                    <button v-if="app.status === 0" class="btn btn-sm btn-outline-danger" @click="withdrawApplication(app.drive_id)">
                                                        Withdraw
                                                    </button>
                                                    <span v-else class="text-muted small">No actions available</span>
                                                </td>
                                            </tr>

                                            <tr v-if="myApplications.length === 0">
                                                <td colspan="5" class="text-center text-muted py-5">
                                                    You have not applied to any placement drives yet.
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
