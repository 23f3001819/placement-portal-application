<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authstore.js';

const props = defineProps({
  id: {
    type: [String, Number],
    required: true
  }
});

const router = useRouter();
const auth_store = useAuthStore();

const applicants = ref([]);
const driveInfo = ref(null);
const errorMessage = ref('');
const isLoading = ref(true);

const fetchApplicants = async () => {
    try {
        isLoading.value = true;
        
        const response = await fetch(`http://127.0.0.1:5000/api/applications/${props.id}`, {
            method: 'GET',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const data = await response.json();
        if (response.ok) {
            applicants.value = data;
        } else {
            errorMessage.value = data.message || "Failed to load applicants.";
        }
    } catch (error) {
        console.error("Error fetching applicants:", error);
        errorMessage.value = "Failed to load applicants due to a network error.";
    } finally {
        isLoading.value = false;
    }
};

const fetchDriveDetails = async () => {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/drives/${props.id}`, {
            method: 'GET',
            headers: {
                'Authorization': auth_store.getAuthToken() || ''
            }
        });
        const data = await response.json();
        if (response.ok) {
            driveInfo.value = data;
        }
    } catch (error) {
        console.error("Error fetching drive details:", error);
    }
};

onMounted(() => {
    fetchDriveDetails();
    fetchApplicants();
});

const updateStatus = async (appId, newStatus) => {
    const statusLabels = {
        0: 'Applied',
        1: 'Shortlisted',
        2: 'Accepted',
        3: 'Rejected'
    };
    const targetLabel = statusLabels[newStatus] || 'Unknown';
    if (!confirm(`Are you sure you want to set this application status to ${targetLabel}?`)) {
        fetchApplicants();
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/manage-application/${appId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': auth_store.getAuthToken() || ''
            },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.message || "Status updated successfully.");
            
            fetchApplicants();
        } else {
            alert(data.message || "Failed to update status.");
        }
    } catch (error) {
        console.error("Error updating application status:", error);
        alert("A network error occurred while updating status.");
    }
};

const getResumeUrl = (path) => {
    if (!path) return null;
    return `http://127.0.0.1:5000/${path}`;
};
</script>

<template>
    <div class="container mt-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <RouterLink to="/company" class="btn btn-outline-secondary btn-sm mb-2">
                    &larr; Back to Dashboard
                </RouterLink>
                <h2 v-if="driveInfo">Applicants for {{ driveInfo.job_role }}</h2>
                <h2 v-else>Drive Applicants</h2>
                <p v-if="driveInfo" class="text-muted mb-0">
                    Drive ID: {{ props.id }} | CTC: {{ driveInfo.job_ctc }} LPA | Minimum CGPA: {{ driveInfo.cgpa_c }}
                </p>
            </div>
            <div>
                <button class="btn btn-outline-primary btn-sm" @click="fetchApplicants">
                    Refresh List
                </button>
            </div>
        </div>

        <div v-if="isLoading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading applicants...</p>
        </div>

        <div v-else>
            <div v-if="errorMessage" class="alert alert-danger">
                {{ errorMessage }}
            </div>

            <div class="card shadow-sm">
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover align-middle mb-0">
                            <thead class="table-dark">
                                <tr>
                                    <th>Student Name</th>
                                    <th>Branch</th>
                                    <th>CGPA</th>
                                    <th>Resume</th>
                                    <th>Status</th>
                                    <th class="text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="app in applicants" :key="app.app_id">
                                    <td><strong>{{ app.student_name }}</strong></td>
                                    <td>{{ app.branch }}</td>
                                    <td>{{ app.cgpa }}</td>
                                    <td>
                                        <a v-if="app.resume_path" :href="getResumeUrl(app.resume_path)" target="_blank" class="btn btn-sm btn-outline-secondary">
                                            View Resume (PDF)
                                        </a>
                                        <span v-else class="text-muted">No resume uploaded</span>
                                    </td>
                                    <td>
                                        <span v-if="app.status === 0" class="badge bg-secondary text-light">Applied</span>
                                        <span v-else-if="app.status === 1" class="badge bg-info text-dark">Shortlisted</span>
                                        <span v-else-if="app.status === 2" class="badge bg-success">Accepted</span>
                                        <span v-else-if="app.status === 3" class="badge bg-danger">Rejected</span>
                                        <span v-else class="badge bg-light text-dark">Unknown ({{ app.status }})</span>
                                    </td>
                                    <td class="text-center">
                                        <select 
                                            class="form-select form-select-sm mx-auto" 
                                            style="max-width: 150px;"
                                            :value="app.status" 
                                            @change="updateStatus(app.app_id, parseInt($event.target.value))"
                                        >
                                            <option :value="0">Applied</option>
                                            <option :value="1">Shortlisted</option>
                                            <option :value="2">Accepted</option>
                                            <option :value="3">Rejected</option>
                                        </select>
                                    </td>
                                </tr>

                                <tr v-if="applicants.length === 0">
                                    <td colspan="6" class="text-center text-muted py-5">
                                        No students have applied to this drive yet.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
